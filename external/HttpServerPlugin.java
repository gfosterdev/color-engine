package net.runelite.client.plugins.httpserver;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import java.awt.*;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.net.InetSocketAddress;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.Semaphore;
import java.util.concurrent.atomic.AtomicReference;
import javax.inject.Inject;
import net.runelite.api.*;
import net.runelite.api.Menu;
import net.runelite.api.Point;
import net.runelite.api.coords.LocalPoint;
import net.runelite.api.coords.WorldPoint;
import net.runelite.api.geometry.SimplePolygon;
import net.runelite.api.widgets.Widget;
import net.runelite.api.gameval.InterfaceID;
import net.runelite.api.widgets.WidgetInfo;
import net.runelite.api.Perspective;
import net.runelite.client.callback.ClientThread;
import net.runelite.client.game.NpcUtil;
import net.runelite.client.plugins.Plugin;
import net.runelite.client.plugins.PluginDescriptor;
import net.runelite.http.api.RuneLiteAPI;

@PluginDescriptor(
        name = "HTTP Server"
)
public class HttpServerPlugin extends Plugin
{
    @Inject
    private Client client;

    @Inject
    private ClientThread clientThread;

    @Inject
    private NpcUtil npcUtil;

    private HttpServer server;

    @Override
    protected void startUp() throws Exception
    {
        server = HttpServer.create(new InetSocketAddress(8080), 0);

        // Player data
        server.createContext("/stats", this::handleStats);
        server.createContext("/player", this::handlePlayer);
        server.createContext("/coords", this::handleCoords);
        server.createContext("/combat", this::handleCombat);
        server.createContext("/animation", this::handleAnimation);

        // Inventory & equipment
        server.createContext("/inv", handlerForInv(InventoryID.INVENTORY));
        // Dynamic inventory slot endpoint, e.g. /inv/5
        server.createContext("/inv/", this::handleInventorySlotDispatcher);

        server.createContext("/equip", handlerForInv(InventoryID.EQUIPMENT));
        server.createContext("/bank", this::handleBank);

        // World data
        server.createContext("/npcs", this::handleNPCs);
        server.createContext("/players", this::handlePlayers);
        server.createContext("/objects", this::handleObjects);
        server.createContext("/grounditems", this::handleGroundItems);
        server.createContext("/npcs_in_viewport", this::getNPCsInViewport);
        server.createContext("/objects_in_viewport", this::getGameObjectsInViewport);
        server.createContext("/find_nearest", this::handleFindNearest);

        // Game state
        server.createContext("/camera", this::handleCamera);
        server.createContext("/camera_rotation", this::handleCameraRotation);
        server.createContext("/game", this::handleGameState);
        server.createContext("/menu", this::handleMenu);
        server.createContext("/widgets", this::handleWidgets);
        server.createContext("/sidebar", this::handleSidebars);
        server.createContext("/sidebar/", this::handleSidebarDispatcher);
        server.createContext("/selected_widget", this::handleSelectedWidget);

        // Client state
        server.createContext("/viewport", this::handleViewport);

        server.setExecutor(Executors.newSingleThreadExecutor());
        server.start();
    }

    @Override
    protected void shutDown() throws Exception
    {
        server.stop(1);
    }

    public void handleViewport(HttpExchange exchange) throws IOException
    {
        JsonObject viewportData = invokeAndWait(() -> {
            JsonObject data = new JsonObject();
            data.addProperty("width", client.getViewportWidth());
            data.addProperty("height", client.getViewportHeight());
            data.addProperty("xOffset", client.getViewportXOffset());
            data.addProperty("yOffset", client.getViewportYOffset());
            Point canvasMousePos = client.getMouseCanvasPosition();
            data.addProperty("canvasMouseX", canvasMousePos != null ? canvasMousePos.getX() : -1);
            data.addProperty("canvasMouseY", canvasMousePos != null ? canvasMousePos.getY() : -1);

            return data;
        });

        exchange.sendResponseHeaders(200, 0);
        try (OutputStreamWriter out = new OutputStreamWriter(exchange.getResponseBody()))
        {
            RuneLiteAPI.GSON.toJson(viewportData, out);
        }
    }

    public void handleStats(HttpExchange exchange) throws IOException
    {
        JsonArray skills = new JsonArray();
        for (Skill skill : Skill.values())
        {
            if (skill == Skill.OVERALL)
            {
                continue;
            }

            int level = client.getRealSkillLevel(skill);
            int boosted = client.getBoostedSkillLevel(skill);
            int xp = client.getSkillExperience(skill);

            JsonObject object = new JsonObject();
            object.addProperty("stat", skill.getName());
            object.addProperty("level", level);
            object.addProperty("boostedLevel", boosted);
            object.addProperty("xp", xp);

            // Calculate XP to next level
            int nextLevelXp = level < 99 ? Experience.getXpForLevel(level + 1) : xp;
            object.addProperty("xpToNextLevel", nextLevelXp - xp);
            object.addProperty("nextLevelAt", nextLevelXp);

            skills.add(object);
        }

        exchange.sendResponseHeaders(200, 0);
        try (OutputStreamWriter out = new OutputStreamWriter(exchange.getResponseBody()))
        {
            RuneLiteAPI.GSON.toJson(skills, out);
        }
    }

    public void handlePlayer(HttpExchange exchange) throws IOException
    {
        JsonObject playerData = invokeAndWait(() -> {
            Player localPlayer = client.getLocalPlayer();
            if (localPlayer == null) return null;

            JsonObject data = new JsonObject();
            data.addProperty("name", localPlayer.getName());
            data.addProperty("combatLevel", localPlayer.getCombatLevel());
            data.addProperty("health", client.getBoostedSkillLevel(Skill.HITPOINTS));
            data.addProperty("maxHealth", client.getRealSkillLevel(Skill.HITPOINTS));
            data.addProperty("prayer", client.getBoostedSkillLevel(Skill.PRAYER));
            data.addProperty("maxPrayer", client.getRealSkillLevel(Skill.PRAYER));
            data.addProperty("runEnergy", client.getEnergy());
            data.addProperty("specialAttack", client.getVarpValue(VarPlayer.SPECIAL_ATTACK_PERCENT) / 10);
            data.addProperty("weight", client.getWeight());
            data.addProperty("isAnimating", localPlayer.getAnimation() != -1);
            data.addProperty("animationId", localPlayer.getAnimation());

            Actor interacting = localPlayer.getInteracting();
            if (interacting != null) {
                data.addProperty("interactingWith", interacting.getName());
            }

            return data;
        });

        sendJsonResponse(exchange, playerData);
    }

    public void handleCombat(HttpExchange exchange) throws IOException
    {
        JsonObject combat = invokeAndWait(() -> {
            Player localPlayer = client.getLocalPlayer();
            if (localPlayer == null) return null;

            JsonObject data = new JsonObject();
            data.addProperty("inCombat", localPlayer.getInteracting() != null);
            data.addProperty("combatLevel", localPlayer.getCombatLevel());
            
            // Auto-retaliate status (VarPlayer 172: 0 = enabled, 1 = disabled)
            data.addProperty("autoRetaliate", client.getVarpValue(172) == 0);
            
            // Poison/venom status (VarPlayer 102 = poison, 1308 = venom)
            int poisonValue = client.getVarpValue(102);
            int venomValue = client.getVarpValue(1308);
            data.addProperty("isPoisoned", poisonValue > 0);
            data.addProperty("isVenomed", venomValue > 0);
            data.addProperty("poisonDamage", poisonValue);
            data.addProperty("venomDamage", venomValue);

            Actor target = localPlayer.getInteracting();
            if (target != null) {
                JsonObject targetData = new JsonObject();
                targetData.addProperty("name", target.getName());

                if (target instanceof NPC) {
                    NPC npc = (NPC) target;
                    targetData.addProperty("id", npc.getId());
                    targetData.addProperty("combatLevel", npc.getCombatLevel());

                    int health = -1;
                    int maxHealth = -1;
                    if (npc.getHealthRatio() != -1) {
                        health = npc.getHealthRatio();
                        maxHealth = npc.getHealthScale();
                    }
                    targetData.addProperty("health", health);
                    targetData.addProperty("maxHealth", maxHealth);
                    targetData.addProperty("isDying", npcUtil.isDying(npc));
                }

                data.add("target", targetData);
            }

            return data;
        });

        sendJsonResponse(exchange, combat);
    }

    public void handleAnimation(HttpExchange exchange) throws IOException
    {
        JsonObject anim = invokeAndWait(() -> {
            Player localPlayer = client.getLocalPlayer();
            if (localPlayer == null) return null;

            JsonObject data = new JsonObject();
            data.addProperty("animationId", localPlayer.getAnimation());
            data.addProperty("poseAnimation", localPlayer.getPoseAnimation());
            data.addProperty("isAnimating", localPlayer.getAnimation() != -1);
            data.addProperty("isMoving", localPlayer.getIdlePoseAnimation() != localPlayer.getPoseAnimation());

            return data;
        });

        sendJsonResponse(exchange, anim);
    }

    public void handleCoords(HttpExchange exchange) throws IOException
    {
        JsonObject coords = invokeAndWait(() -> {
            Player localPlayer = client.getLocalPlayer();
            if (localPlayer == null)
            {
                return null;
            }

            JsonObject coordData = new JsonObject();

            // World coordinates
            WorldPoint worldLocation = localPlayer.getWorldLocation();
            JsonObject worldCoords = new JsonObject();
            worldCoords.addProperty("x", worldLocation.getX());
            worldCoords.addProperty("y", worldLocation.getY());
            worldCoords.addProperty("plane", worldLocation.getPlane());
            worldCoords.addProperty("regionID", worldLocation.getRegionID());
            worldCoords.addProperty("regionX", worldLocation.getRegionX());
            worldCoords.addProperty("regionY", worldLocation.getRegionY());
            coordData.add("world", worldCoords);

            // Local coordinates
            LocalPoint localLocation = localPlayer.getLocalLocation();
            JsonObject localCoords = new JsonObject();
            localCoords.addProperty("x", localLocation.getX());
            localCoords.addProperty("y", localLocation.getY());
            localCoords.addProperty("sceneX", localLocation.getSceneX());
            localCoords.addProperty("sceneY", localLocation.getSceneY());
            coordData.add("local", localCoords);

            return coordData;
        });

        sendJsonResponse(exchange, coords);
    }

    public void getGameObjectsInViewport(HttpExchange exchange) throws IOException
    {
        JsonArray objectsData = invokeAndWait(() -> {
            JsonArray objects = new JsonArray();
            Scene scene = client.getScene();
            Tile[][][] tiles = scene.getTiles();
            int plane = client.getPlane();
            
            // Track seen game objects to avoid duplicates based on id, worldX, worldY
            java.util.Set<String> seenObjects = new java.util.HashSet<>();

            for (int x = 0; x < 104; x++)
            {
                for (int y = 0; y < 104; y++)
                {
                    Tile tile = tiles[plane][x][y];
                    if (tile == null) continue;
                    Point tilePoint = Perspective.localToCanvas(client, tile.getLocalLocation(), plane);
                    if (!isPointInViewport(tilePoint)) continue;

                    for (GameObject gameObject : tile.getGameObjects())
                    {
                        if (gameObject == null) continue;

                        WorldPoint wp = gameObject.getWorldLocation();
                        
                        // Create unique key from id, worldX, worldY
                        String objectKey = gameObject.getId() + "_" + wp.getX() + "_" + wp.getY();
                        
                        // Skip if we've already added this object
                        if (seenObjects.contains(objectKey)) {
                            continue;
                        }
                        seenObjects.add(objectKey);

                        Point point = Perspective.localToCanvas(client, gameObject.getLocalLocation(), plane);
                        JsonObject objData = new JsonObject();
                        objData.addProperty("id", gameObject.getId());
                        objData.addProperty("worldX", wp.getX());
                        objData.addProperty("worldY", wp.getY());
                        objData.addProperty("x", point.getX());
                        objData.addProperty("y", point.getY());

                        SimplePolygon hull = (SimplePolygon) gameObject.getConvexHull();
                        JsonObject hullData = new JsonObject();
                        hullData.addProperty("exists", hull != null);
                        if (hull != null) {
                            JsonArray pointData = new JsonArray();
                            List<Point> points = hull.toRuneLitePointList();
                            for (Point value : points) {
                                JsonObject pointObj = new JsonObject();
                                pointObj.addProperty("x", value.getX());
                                pointObj.addProperty("y", value.getY());
                                pointData.add(pointObj);
                            }
                            hullData.add("points", pointData);
                        }

                        objData.add("hull", hullData);

                        objects.add(objData);
                    }
                }
            }

            return objects;
        });

        exchange.sendResponseHeaders(200, 0);
        try (OutputStreamWriter out = new OutputStreamWriter(exchange.getResponseBody()))
        {
            RuneLiteAPI.GSON.toJson(objectsData, out);
        }
    }

    public boolean isPointInViewport(Point point)
    {
        return point != null
                && point.getX() >= 0 && point.getX() <= client.getViewportWidth()
                && point.getY() >= 0 && point.getY() <= client.getViewportHeight();
    }

    public void handleFindNearest(HttpExchange exchange) throws IOException
    {
        // Parse query parameters: /find_nearest?ids=1234,5678&type=npc
        String query = exchange.getRequestURI().getQuery();
        if (query == null)
        {
            exchange.sendResponseHeaders(400, 0);
            exchange.getResponseBody().close();
            return;
        }

        Map<String, String> params = new java.util.HashMap<>();
        for (String param : query.split("&"))
        {
            String[] pair = param.split("=");
            if (pair.length == 2)
            {
                params.put(pair[0], pair[1]);
            }
        }

        if (!params.containsKey("ids") || !params.containsKey("type"))
        {
            exchange.sendResponseHeaders(400, 0);
            exchange.getResponseBody().close();
            return;
        }

        int[] targetIds;
        String searchType = params.get("type").toLowerCase();
        
        if (!searchType.equals("npc") && !searchType.equals("object"))
        {
            exchange.sendResponseHeaders(400, 0);
            exchange.getResponseBody().close();
            return;
        }
        
        try
        {
            String[] idStrings = params.get("ids").split(",");
            targetIds = new int[idStrings.length];
            for (int i = 0; i < idStrings.length; i++)
            {
                targetIds[i] = Integer.parseInt(idStrings[i].trim());
            }
        }
        catch (NumberFormatException ex)
        {
            exchange.sendResponseHeaders(400, 0);
            exchange.getResponseBody().close();
            return;
        }

        JsonObject result = invokeAndWait(() -> {
            Player localPlayer = client.getLocalPlayer();
            if (localPlayer == null) return null;

            WorldPoint playerPos = localPlayer.getWorldLocation();
            JsonObject data = new JsonObject();
            
            // Convert targetIds array to JsonArray for response
            JsonArray searchIdsArray = new JsonArray();
            for (int id : targetIds)
            {
                searchIdsArray.add(id);
            }
            data.add("searchIds", searchIdsArray);
            data.addProperty("searchType", searchType);
            data.addProperty("found", false);

            if (searchType.equals("npc"))
            {
                // Search for NPCs matching any of the target IDs
                NPC closestNPC = null;
                int closestNPCDistance = Integer.MAX_VALUE;
                List<NPC> npcList = client.getNpcs();

                for (NPC npc : npcList)
                {
                    if (npc == null) continue;
                    
                    // Filter out NPCs that are interacting with anything
                    Actor interacting = npc.getInteracting();
                    if (interacting != null) continue;
                    
                    // Check if NPC ID matches any of the target IDs
                    boolean matches = false;
                    for (int targetId : targetIds)
                    {
                        if (npc.getId() == targetId)
                        {
                            matches = true;
                            break;
                        }
                    }
                    
                    if (!matches) continue;

                    WorldPoint npcPos = npc.getWorldLocation();
                    int distance = npcPos.distanceTo(playerPos);

                    if (distance < closestNPCDistance)
                    {
                        closestNPC = npc;
                        closestNPCDistance = distance;
                    }
                }

                if (closestNPC != null)
                {
                    WorldPoint npcPos = closestNPC.getWorldLocation();
                    data.addProperty("found", true);
                    data.addProperty("type", "npc");
                    data.addProperty("name", closestNPC.getName());
                    data.addProperty("id", closestNPC.getId());
                    data.addProperty("worldX", npcPos.getX());
                    data.addProperty("worldY", npcPos.getY());
                    data.addProperty("plane", npcPos.getPlane());
                    data.addProperty("distance", closestNPCDistance);
                }
            }
            else if (searchType.equals("object"))
            {
                // Search for game objects matching any of the target IDs
                GameObject closestObject = null;
                int closestObjectDistance = Integer.MAX_VALUE;
                Scene scene = client.getScene();
                Tile[][][] tiles = scene.getTiles();
                int plane = client.getPlane();

                for (int x = 0; x < 104; x++)
                {
                    for (int y = 0; y < 104; y++)
                    {
                        Tile tile = tiles[plane][x][y];
                        if (tile == null) continue;

                        for (GameObject gameObject : tile.getGameObjects())
                        {
                            if (gameObject == null) continue;
                            
                            // Check if object ID matches any of the target IDs
                            boolean matches = false;
                            for (int targetId : targetIds)
                            {
                                if (gameObject.getId() == targetId)
                                {
                                    matches = true;
                                    break;
                                }
                            }
                            
                            if (!matches) continue;

                            WorldPoint objPos = gameObject.getWorldLocation();
                            int distance = objPos.distanceTo(playerPos);

                            if (distance < closestObjectDistance)
                            {
                                closestObject = gameObject;
                                closestObjectDistance = distance;
                            }
                        }
                    }
                }

                if (closestObject != null)
                {
                    WorldPoint objPos = closestObject.getWorldLocation();
                    data.addProperty("found", true);
                    data.addProperty("type", "object");
                    data.addProperty("id", closestObject.getId());
                    data.addProperty("worldX", objPos.getX());
                    data.addProperty("worldY", objPos.getY());
                    data.addProperty("plane", objPos.getPlane());
                    data.addProperty("distance", closestObjectDistance);
                }
            }

            return data;
        });

        sendJsonResponse(exchange, result);
    }

    public void getNPCsInViewport(HttpExchange exchange) throws IOException
    {
        JsonArray npcsData = invokeAndWait(() -> {
            JsonArray npcs = new JsonArray();
            List<NPC> npcList = client.getNpcs();
            
            // Track seen NPCs to avoid duplicates based on id, worldX, worldY
            java.util.Set<String> seenNPCs = new java.util.HashSet<>();

            for (NPC npc : npcList)
            {
                if (npc == null) continue;

                WorldPoint wp = npc.getWorldLocation();
                LocalPoint lp = npc.getLocalLocation();
                Point point = Perspective.localToCanvas(client, lp, wp.getPlane());
                if (isPointInViewport(point))
                {
                    // Create unique key from id, worldX, worldY
                    String npcKey = npc.getId() + "_" + wp.getX() + "_" + wp.getY();
                    
                    // Skip if we've already added this NPC
                    if (seenNPCs.contains(npcKey)) {
                        continue;
                    }
                    seenNPCs.add(npcKey);
                    
                    JsonObject npcData = new JsonObject();
                    npcData.addProperty("name", npc.getName());
                    npcData.addProperty("id", npc.getId());
                    npcData.addProperty("worldX", wp.getX());
                    npcData.addProperty("worldY", wp.getY());
                    npcData.addProperty("x", point.getX());
                    npcData.addProperty("y", point.getY());
                    npcData.addProperty("combatLevel", npc.getCombatLevel());
                    
                    // Enhanced Actor data
                    Actor interacting = npc.getInteracting();
                    if (interacting != null) {
                        npcData.addProperty("interactingWith", interacting.getName());
                    } else {
                        npcData.addProperty("interactingWith", (String) null);
                    }
                    npcData.addProperty("isDying", npcUtil.isDying(npc));
                    npcData.addProperty("animation", npc.getAnimation());
                    npcData.addProperty("graphicId", npc.getGraphic());
                    npcData.addProperty("overheadText", npc.getOverheadText());
                    
                    // Health data
                    if (npc.getHealthRatio() != -1) {
                        npcData.addProperty("healthRatio", npc.getHealthRatio());
                        npcData.addProperty("healthScale", npc.getHealthScale());
                    }

                    SimplePolygon hull = (SimplePolygon) npc.getConvexHull();
                    JsonObject hullData = new JsonObject();
                    hullData.addProperty("exists", hull != null);
                    if (hull != null) {
                        JsonArray pointData = new JsonArray();
                        List<Point> points = hull.toRuneLitePointList();
                        for (Point value : points) {
                            JsonObject pointObj = new JsonObject();
                            pointObj.addProperty("x", value.getX());
                            pointObj.addProperty("y", value.getY());
                            pointData.add(pointObj);
                        }
                        hullData.add("points", pointData);
                    }

                    npcData.add("hull", hullData);

                    npcs.add(npcData);
                }
            }

            return npcs;
        });

        exchange.sendResponseHeaders(200, 0);
        try (OutputStreamWriter out = new OutputStreamWriter(exchange.getResponseBody()))
        {
            RuneLiteAPI.GSON.toJson(npcsData, out);
        }
    }

    public void handleNPCs(HttpExchange exchange) throws IOException
    {
        JsonArray npcsData = invokeAndWait(() -> {
            JsonArray npcs = new JsonArray();
            List<NPC> npcList = client.getNpcs();

            for (NPC npc : npcList)
            {
                if (npc == null) continue;

                JsonObject npcData = new JsonObject();
                npcData.addProperty("name", npc.getName());
                npcData.addProperty("id", npc.getId());
                npcData.addProperty("combatLevel", npc.getCombatLevel());
                npcData.addProperty("index", npc.getIndex());

                WorldPoint wp = npc.getWorldLocation();
                JsonObject pos = new JsonObject();
                pos.addProperty("x", wp.getX());
                pos.addProperty("y", wp.getY());
                pos.addProperty("plane", wp.getPlane());
                npcData.add("position", pos);

                LocalPoint lp = npc.getLocalLocation();
                npcData.addProperty("distanceFromPlayer",
                        lp != null && client.getLocalPlayer() != null && client.getLocalPlayer().getLocalLocation() != null
                                ? lp.distanceTo(client.getLocalPlayer().getLocalLocation()) / 128
                                : -1);

                if (npc.getHealthRatio() != -1) {
                    npcData.addProperty("healthRatio", npc.getHealthRatio());
                    npcData.addProperty("healthScale", npc.getHealthScale());
                }

                npcData.addProperty("animation", npc.getAnimation());
                npcData.addProperty("isInteracting", npc.getInteracting() != null);

                npcs.add(npcData);
            }

            return npcs;
        });

        exchange.sendResponseHeaders(200, 0);
        try (OutputStreamWriter out = new OutputStreamWriter(exchange.getResponseBody()))
        {
            RuneLiteAPI.GSON.toJson(npcsData, out);
        }
    }

    /** Dispatcher for dynamic /inv/{slot} routes. */
    public void handleInventorySlotDispatcher(HttpExchange exchange) throws IOException
    {
        String path = exchange.getRequestURI().getPath();
        // Expecting path like /inv/{slot}
        String prefix = "/inv/";
        if (!path.startsWith(prefix))
        {
            exchange.sendResponseHeaders(404, 0);
            exchange.getResponseBody().close();
            return;
        }

        String after = path.substring(prefix.length());
        if (after.isEmpty())
        {
            exchange.sendResponseHeaders(400, 0);
            exchange.getResponseBody().close();
            return;
        }

        // Only consider the first path segment after /inv/
        String[] parts = after.split("/");
        String slotStr = parts[0];

        int slot;
        try
        {
            slot = Integer.parseInt(slotStr);
        }
        catch (NumberFormatException ex)
        {
            exchange.sendResponseHeaders(400, 0);
            exchange.getResponseBody().close();
            return;
        }

        handleInventorySlot(exchange, slot);
    }

    /** Handle a specific inventory slot. */
    public void handleInventorySlot(HttpExchange exchange, int slot) throws IOException
    {
        JsonObject slotData = invokeAndWait(() -> {
            JsonObject data = new JsonObject();
            data.addProperty("requestedSlot", slot);

            ItemContainer inv = client.getItemContainer(InventoryID.INVENTORY);
            int idx = slot - 1; // convert to 0-based index for ItemContainer
            Item item = inv.getItem(idx);

            if (item == null || item.getId() == -1)
            {
                data.addProperty("empty", true);
                return data;
            }

            data.addProperty("empty", false);
            data.addProperty("itemId", item.getId());
            data.addProperty("quantity", item.getQuantity());

            return data;
        });

        sendJsonResponse(exchange, slotData);
    }

    public void handlePlayers(HttpExchange exchange) throws IOException
    {
        JsonArray playersData = invokeAndWait(() -> {
            JsonArray players = new JsonArray();
            List<Player> playerList = client.getPlayers();

            for (Player player : playerList)
            {
                if (player == null || player == client.getLocalPlayer()) continue;

                JsonObject playerData = new JsonObject();
                playerData.addProperty("name", player.getName());
                playerData.addProperty("combatLevel", player.getCombatLevel());

                WorldPoint wp = player.getWorldLocation();
                JsonObject pos = new JsonObject();
                pos.addProperty("x", wp.getX());
                pos.addProperty("y", wp.getY());
                pos.addProperty("plane", wp.getPlane());
                playerData.add("position", pos);

                playerData.addProperty("animation", player.getAnimation());
                playerData.addProperty("team", player.getTeam());
                playerData.addProperty("isFriend", player.isFriend());

                players.add(playerData);
            }

            return players;
        });

        exchange.sendResponseHeaders(200, 0);
        try (OutputStreamWriter out = new OutputStreamWriter(exchange.getResponseBody()))
        {
            RuneLiteAPI.GSON.toJson(playersData, out);
        }
    }

    public void handleObjects(HttpExchange exchange) throws IOException
    {
        JsonArray objectsData = invokeAndWait(() -> {
            JsonArray objects = new JsonArray();
            Scene scene = client.getScene();
            Tile[][][] tiles = scene.getTiles();
            int plane = client.getPlane();

            for (int x = 0; x < 104; x++)
            {
                for (int y = 0; y < 104; y++)
                {
                    Tile tile = tiles[plane][x][y];
                    if (tile == null) continue;

                    for (GameObject gameObject : tile.getGameObjects())
                    {
                        if (gameObject == null) continue;

                        JsonObject objData = new JsonObject();
                        objData.addProperty("id", gameObject.getId());

                        WorldPoint wp = gameObject.getWorldLocation();
                        JsonObject pos = new JsonObject();
                        pos.addProperty("x", wp.getX());
                        pos.addProperty("y", wp.getY());
                        pos.addProperty("plane", wp.getPlane());
                        objData.add("position", pos);

                        objects.add(objData);
                    }
                }
            }

            return objects;
        });

        exchange.sendResponseHeaders(200, 0);
        try (OutputStreamWriter out = new OutputStreamWriter(exchange.getResponseBody()))
        {
            RuneLiteAPI.GSON.toJson(objectsData, out);
        }
    }

    public void handleGroundItems(HttpExchange exchange) throws IOException
    {
        JsonArray itemsData = invokeAndWait(() -> {
            JsonArray items = new JsonArray();
            Scene scene = client.getScene();
            Tile[][][] tiles = scene.getTiles();
            int plane = client.getPlane();

            for (int x = 0; x < 104; x++)
            {
                for (int y = 0; y < 104; y++)
                {
                    Tile tile = tiles[plane][x][y];
                    if (tile == null) continue;

                    for (TileItem tileItem : tile.getGroundItems())
                    {
                        if (tileItem == null) continue;

                        JsonObject itemData = new JsonObject();
                        itemData.addProperty("id", tileItem.getId());
                        itemData.addProperty("quantity", tileItem.getQuantity());

                        WorldPoint wp = tile.getWorldLocation();
                        JsonObject pos = new JsonObject();
                        pos.addProperty("x", wp.getX());
                        pos.addProperty("y", wp.getY());
                        pos.addProperty("plane", wp.getPlane());
                        itemData.add("position", pos);

                        items.add(itemData);
                    }
                }
            }

            return items;
        });

        exchange.sendResponseHeaders(200, 0);
        try (OutputStreamWriter out = new OutputStreamWriter(exchange.getResponseBody()))
        {
            RuneLiteAPI.GSON.toJson(itemsData, out);
        }
    }

    public void handleCamera(HttpExchange exchange) throws IOException
    {
        JsonObject cameraData = invokeAndWait(() -> {
            JsonObject data = new JsonObject();
            data.addProperty("yaw", client.getCameraYaw());
            data.addProperty("pitch", client.getCameraPitch());
            data.addProperty("scale", client.getScale());
            data.addProperty("x", client.getCameraX());
            data.addProperty("y", client.getCameraY());
            data.addProperty("z", client.getCameraZ());

            return data;
        });

        sendJsonResponse(exchange, cameraData);
    }

    public void handleCameraRotation(HttpExchange exchange) throws IOException
    {
        // Parse query parameters: /camera_rotation?x=3222&y=3218&plane=0
        String query = exchange.getRequestURI().getQuery();
        if (query == null)
        {
            exchange.sendResponseHeaders(400, 0);
            exchange.getResponseBody().close();
            return;
        }

        Map<String, String> params = new java.util.HashMap<>();
        for (String param : query.split("&"))
        {
            String[] pair = param.split("=");
            if (pair.length == 2)
            {
                params.put(pair[0], pair[1]);
            }
        }

        if (!params.containsKey("x") || !params.containsKey("y"))
        {
            exchange.sendResponseHeaders(400, 0);
            exchange.getResponseBody().close();
            return;
        }

        int targetX, targetY, targetPlane;
        try
        {
            targetX = Integer.parseInt(params.get("x"));
            targetY = Integer.parseInt(params.get("y"));
            targetPlane = params.containsKey("plane") ? Integer.parseInt(params.get("plane")) : 0;
        }
        catch (NumberFormatException ex)
        {
            exchange.sendResponseHeaders(400, 0);
            exchange.getResponseBody().close();
            return;
        }

        JsonObject rotationData = invokeAndWait(() -> {
            Player localPlayer = client.getLocalPlayer();
            if (localPlayer == null) return null;

            WorldPoint playerPos = localPlayer.getWorldLocation();
            WorldPoint targetTile = new WorldPoint(targetX, targetY, targetPlane);

            JsonObject data = new JsonObject();

            // Check if tile is visible in viewport
            LocalPoint localTarget = LocalPoint.fromWorld(client, targetTile);
            boolean isVisible = false;
            Point screenPoint = null;

            if (localTarget != null)
            {
                screenPoint = Perspective.localToCanvas(client, localTarget, targetPlane);
                if (screenPoint != null)
                {
                    isVisible = isPointInViewport(screenPoint);
                    data.addProperty("screenX", screenPoint.getX());
                    data.addProperty("screenY", screenPoint.getY());
                }
            }

            data.addProperty("visible", isVisible);

            // Get current camera state
            int currentYaw = client.getCameraYaw();
            int currentPitch = client.getCameraPitch();
            int currentScale = client.getScale();
            data.addProperty("currentYaw", currentYaw);
            data.addProperty("currentPitch", currentPitch);
            data.addProperty("currentScale", currentScale);

            // Get viewport dimensions and center
            int viewportWidth = client.getViewportWidth();
            int viewportHeight = client.getViewportHeight();
            int centerX = viewportWidth / 2;
            int centerY = viewportHeight / 2;
            data.addProperty("viewportCenterX", centerX);
            data.addProperty("viewportCenterY", centerY);

            // Calculate target yaw/pitch/scale to center the tile
            int targetYaw;
            int targetPitch;
            int targetScale;
            
            // Calculate distance for scale calculation
            int dx = targetX - playerPos.getX();
            int dy = targetY - playerPos.getY();
            double distanceToTarget = Math.sqrt(dx * dx + dy * dy);
            
            if (isVisible && screenPoint != null)
            {
                // Tile is visible - calculate adjustments to center it
                int offsetX = screenPoint.getX() - centerX;
                int offsetY = screenPoint.getY() - centerY;
                data.addProperty("offsetFromCenterX", offsetX);
                data.addProperty("offsetFromCenterY", offsetY);
                
                // Convert pixel offsets to camera angle adjustments
                // These conversion factors are empirically tuned for OSRS camera behavior
                // Positive offsetX = tile is right of center, need to rotate camera right (increase yaw)
                // Positive offsetY = tile is below center, need to tilt camera down (increase pitch)
                double pixelsPerYawUnit = 3.0;
                double pixelsPerPitchUnit = 2.5;
                
                int yawAdjustment = (int)(offsetX / pixelsPerYawUnit);
                int pitchAdjustment = (int)(offsetY / pixelsPerPitchUnit);
                
                targetYaw = (currentYaw + yawAdjustment) % 2048;
                if (targetYaw < 0) targetYaw += 2048;
                
                targetPitch = currentPitch + pitchAdjustment;
                targetPitch = Math.max(128, Math.min(383, targetPitch));
                
                data.addProperty("usingCenteredCalculation", true);
            }
            else
            {
                // Tile not visible - calculate yaw to face tile and pitch based on distance
                // Calculate angle in radians (atan2 returns -π to π)
                double angleRadians = Math.atan2(dy, dx);
                
                // Convert to OSRS yaw units (0-2048)
                // OSRS: 0 = North, 512 = West, 1024 = South, 1536 = East (clockwise from North)
                // Standard atan2: 0 = East, π/2 = North, π = West, -π/2 = South
                // Rotate coordinate system by π/2 to change origin from East to North
                double adjustedRadians = angleRadians - Math.PI / 2;
                targetYaw = (int)((adjustedRadians * 2048) / (2 * Math.PI)) % 2048;
                if (targetYaw < 0) targetYaw += 2048;
                
                // Calculate pitch based on distance
                // For ground tiles: closer = look down more, farther = look more horizontal
                // Pitch range: 128 (looking straight down) to 383 (horizontal)
                // Lower pitch values = camera tilted down more to see ground
                if (distanceToTarget < 5)
                {
                    targetPitch = 200;  // Very close, look down steeply
                }
                else if (distanceToTarget < 10)
                {
                    targetPitch = 240;  // Close, look down moderately
                }
                else if (distanceToTarget < 15)
                {
                    targetPitch = 280;  // Medium-close distance
                }
                else if (distanceToTarget < 20)
                {
                    targetPitch = 320;  // Medium-far distance
                }
                else
                {
                    targetPitch = 360;  // Far, look mostly horizontal
                }
                targetPitch = Math.max(128, Math.min(383, targetPitch));
                
                data.addProperty("usingCenteredCalculation", false);
                data.addProperty("dx", dx);
                data.addProperty("dy", dy);
                data.addProperty("angleRadians", angleRadians);
            }
            
            // Calculate target scale based on distance (same for both cases)
            // Zoom out more aggressively to ensure tiles are visible
            // Closer tiles = moderate zoom (400-500), farther tiles = zoomed out (300)
            targetScale = (int)(550 - (distanceToTarget * 20));
            if (distanceToTarget > 12)
            {
                targetScale = 300;  // Max zoom out for distant tiles
            }
            targetScale = Math.max(300, Math.min(650, targetScale));
            
            // Output target values
            data.addProperty("targetYaw", targetYaw);
            data.addProperty("targetPitch", targetPitch);
            data.addProperty("targetScale", targetScale);

            // Calculate deltas from current state
            int clockwise = (targetYaw - currentYaw + 2048) % 2048;
            int counterClockwise = (currentYaw - targetYaw + 2048) % 2048;
            int yawDistance = (clockwise <= counterClockwise) ? clockwise : -counterClockwise;
            int pitchDistance = targetPitch - currentPitch;
            int scaleDelta = targetScale - currentScale;
            
            data.addProperty("yawDistance", yawDistance);
            data.addProperty("pitchDistance", pitchDistance);
            data.addProperty("scaleDelta", scaleDelta);

            // Convert to drag pixels for mouse control using empirical ratios
            // Ratios: 253px per 512 yaw units, 69px per 128 pitch units
            // Apply minimum threshold (8px) to ensure small adjustments execute
            // IMPORTANT: Middle-mouse drag is inverted
            // Positive dragPixelsX = drag left to rotate camera right (clockwise)
            // Negative dragPixelsX = drag right to rotate camera left (counter-clockwise)
            // Positive dragPixelsY = drag down (pitch down), negative = drag up (pitch up)
            
            // Calculate drag using empirical ratio
            int dragPixelsX = (int)((yawDistance / 512.0) * 253);
            int dragPixelsY = (int)((pitchDistance / 128.0) * 69);
            
            // Apply minimum threshold to ensure small adjustments execute (game threshold ~5px)
            if (yawDistance != 0 && Math.abs(dragPixelsX) < 8) {
                dragPixelsX = yawDistance > 0 ? 8 : -8;
            }
            if (pitchDistance != 0 && Math.abs(dragPixelsY) < 8) {
                dragPixelsY = pitchDistance > 0 ? 8 : -8;
            }
            
            // Invert horizontal for middle-mouse behavior (drag right = camera left)
            dragPixelsX = -dragPixelsX;
            
            data.addProperty("dragPixelsX", dragPixelsX);
            data.addProperty("dragPixelsY", dragPixelsY);

            return data;
        });

        sendJsonResponse(exchange, rotationData);
    }

    public void handleGameState(HttpExchange exchange) throws IOException
    {
        JsonObject gameData = invokeAndWait(() -> {
            JsonObject data = new JsonObject();
            data.addProperty("state", client.getGameState().toString());
            data.addProperty("isLoggedIn", client.getGameState() == GameState.LOGGED_IN);
            data.addProperty("world", client.getWorld());
            data.addProperty("gameCycle", client.getGameCycle());
            data.addProperty("tickCount", client.getTickCount());
            data.addProperty("fps", client.getFPS());

            return data;
        });

        sendJsonResponse(exchange, gameData);
    }

    public void handleMenu(HttpExchange exchange) throws IOException
    {
        JsonObject menuData = invokeAndWait(() -> {
            JsonObject menu = new JsonObject();
            Menu clientMenu = client.getMenu();

            menu.addProperty("isOpen", client.isMenuOpen());
            menu.addProperty("x", clientMenu.getMenuX());
            menu.addProperty("y", clientMenu.getMenuY());
            menu.addProperty("width", clientMenu.getMenuWidth());
            menu.addProperty("height", clientMenu.getMenuHeight());

            // Entries
            JsonArray entriesArray = new JsonArray();
            MenuEntry[] entries = clientMenu.getMenuEntries();
            for (MenuEntry entry : entries)
            {
                JsonObject menuEntry = new JsonObject();
                menuEntry.addProperty("option", entry.getOption());
                menuEntry.addProperty("target", entry.getTarget());
                menuEntry.addProperty("type", entry.getType().toString());
                entriesArray.add(menuEntry);
            }
            menu.add("entries", entriesArray);

            return menu;
        });

        exchange.sendResponseHeaders(200, 0);
        try (OutputStreamWriter out = new OutputStreamWriter(exchange.getResponseBody()))
        {
            RuneLiteAPI.GSON.toJson(menuData, out);
        }
    }

    public boolean isSidebarOpen(int sidebarID)
    {
        Widget sidebarWidget = client.getWidget(sidebarID);
        return sidebarWidget != null && !sidebarWidget.isHidden();
    }

    /** Dispatcher for dynamic /sidebar/{sidebarName} routes. */
    public void handleSidebarDispatcher(HttpExchange exchange) throws IOException
    {
        String path = exchange.getRequestURI().getPath();
        // Expecting path like /inv/{slot}
        String prefix = "/sidebar/";
        if (!path.startsWith(prefix))
        {
            exchange.sendResponseHeaders(404, 0);
            exchange.getResponseBody().close();
            return;
        }

        String after = path.substring(prefix.length());
        if (after.isEmpty())
        {
            exchange.sendResponseHeaders(400, 0);
            exchange.getResponseBody().close();
            return;
        }

        // Only consider the first path segment after /inv/
        String[] parts = after.split("/");
        String sidebarStr = parts[0];

        handleInventorySlot(exchange, sidebarStr);
    }

    public void handleInventorySlot(HttpExchange exchange, String sidebarName) throws IOException
    {
        JsonObject sidebarData = invokeAndWait(() -> {
            JsonObject data = new JsonObject();
            data.addProperty("requestedSidebar", sidebarName);

            Integer sidebarID = null;
            String key = sidebarName != null ? sidebarName.toLowerCase() : "";
            switch (key)
            {
                case "combat":
                    sidebarID = InterfaceID.Toplevel.SIDE0;
                    break;
                case "skills":
                    sidebarID = InterfaceID.Toplevel.SIDE1;
                    break;
                case "summary":
                    sidebarID = InterfaceID.Toplevel.SIDE2;
                    break;
                case "inventory":
                    sidebarID = InterfaceID.Toplevel.SIDE3;
                    break;
                case "equipment":
                    sidebarID = InterfaceID.Toplevel.SIDE4;
                    break;
                case "prayer":
                    sidebarID = InterfaceID.Toplevel.SIDE5;
                    break;
                case "magic":
                    sidebarID = InterfaceID.Toplevel.SIDE6;
                    break;
                case "grouping":
                    sidebarID = InterfaceID.Toplevel.SIDE7;
                    break;
                case "account":
                    sidebarID = InterfaceID.Toplevel.SIDE8;
                    break;
                case "friends":
                    sidebarID = InterfaceID.Toplevel.SIDE9;
                    break;
                case "logout":
                    sidebarID = InterfaceID.Toplevel.SIDE10;
                    break;
                case "settings":
                    sidebarID = InterfaceID.Toplevel.SIDE11;
                    break;
                case "emotes":
                    sidebarID = InterfaceID.Toplevel.SIDE12;
                    break;
                case "music":
                    sidebarID = InterfaceID.Toplevel.SIDE13;
                    break;
                default:
                    sidebarID = null;
                    break;
            }

            if (sidebarID == null)
            {
                data.addProperty("error", "Unknown sidebar name");
                return data;
            }

            data.addProperty("isOpen", isSidebarOpen(sidebarID));

            return data;
        });

        sendJsonResponse(exchange, sidebarData);
    }

    public void handleSidebars(HttpExchange exchange) throws IOException
    {
        JsonObject sidebarsData = invokeAndWait(() -> {
            JsonObject data = new JsonObject();

            // UI Inventory tabs
            Map<String, Integer> uiItems = new java.util.HashMap<>();
            uiItems.put("combat", InterfaceID.Toplevel.SIDE0);
            uiItems.put("skills", InterfaceID.Toplevel.SIDE1);
            uiItems.put("summary", InterfaceID.Toplevel.SIDE2);
            uiItems.put("inventory", InterfaceID.Toplevel.SIDE3);
            uiItems.put("equipment", InterfaceID.Toplevel.SIDE4);
            uiItems.put("prayer", InterfaceID.Toplevel.SIDE5);
            uiItems.put("magic", InterfaceID.Toplevel.SIDE6);
            uiItems.put("grouping", InterfaceID.Toplevel.SIDE7);
            uiItems.put("friends", InterfaceID.Toplevel.SIDE9);
            uiItems.put("account", InterfaceID.Toplevel.SIDE8);
            uiItems.put("logout", InterfaceID.Toplevel.SIDE10);
            uiItems.put("settings", InterfaceID.Toplevel.SIDE11);
            uiItems.put("emotes", InterfaceID.Toplevel.SIDE12);
            uiItems.put("music", InterfaceID.Toplevel.SIDE13);

            // Populate sidebar state properties from the map
            for (java.util.Map.Entry<String, Integer> e : uiItems.entrySet())
            {
                data.addProperty(e.getKey(), isSidebarOpen(e.getValue()));
            }

            return data;
        });

        sendJsonResponse(exchange, sidebarsData);
    }

    public void handleWidgets(HttpExchange exchange) throws IOException
    {
        JsonObject widgetsData = invokeAndWait(() -> {
            JsonObject data = new JsonObject();

            // Check common interfaces
            data.addProperty("isBankOpen", client.getWidget(WidgetInfo.BANK_CONTAINER) != null);

            // UI Inventory tabs
            Map<String, Integer> uiItems = new java.util.HashMap<>();
            uiItems.put("combat", InterfaceID.Toplevel.SIDE0);
            uiItems.put("skills", InterfaceID.Toplevel.SIDE1);
            uiItems.put("summary", InterfaceID.Toplevel.SIDE2);
            uiItems.put("inventory", InterfaceID.Toplevel.SIDE3);
            uiItems.put("equipment", InterfaceID.Toplevel.SIDE4);
            uiItems.put("prayer", InterfaceID.Toplevel.SIDE5);
            uiItems.put("magic", InterfaceID.Toplevel.SIDE6);
            uiItems.put("grouping", InterfaceID.Toplevel.SIDE7);
            uiItems.put("friends", InterfaceID.Toplevel.SIDE9);
            uiItems.put("account", InterfaceID.Toplevel.SIDE8);
            uiItems.put("logout", InterfaceID.Toplevel.SIDE10);
            uiItems.put("settings", InterfaceID.Toplevel.SIDE11);
            uiItems.put("emotes", InterfaceID.Toplevel.SIDE12);
            uiItems.put("music", InterfaceID.Toplevel.SIDE13);

            // Login screen
            uiItems.put("login_click_to_play", InterfaceID.WELCOME_SCREEN);

            // Populate widget state properties from the map
            for (java.util.Map.Entry<String, Integer> e : uiItems.entrySet())
            {
                data.addProperty(e.getKey(), isSidebarOpen(e.getValue()));
            }

            return data;
        });

        sendJsonResponse(exchange, widgetsData);
    }

    public void handleSelectedWidget(HttpExchange exchange) throws IOException
    {
        JsonObject selectedData = invokeAndWait(() -> {
            JsonObject data = new JsonObject();
            
            // Get the selected widget (spell) ID
            // This is used to detect when a spell has been selected and is awaiting a target
            // (e.g., High Alchemy, Telekinetic Grab, etc.)
            Widget selectedWidget = client.getSelectedWidget();
            
            if (selectedWidget != null)
            {
                data.addProperty("selectedWidgetId", selectedWidget.getId());
                data.addProperty("selectedWidgetName", selectedWidget.getName());
                data.addProperty("hasSelection", true);
                
                // Try to extract spell information if it's a magic spell
                // The widget ID can be parsed to determine the specific spell
                int widgetId = selectedWidget.getId();
                data.addProperty("widgetIdPacked", widgetId);
                
                // Unpack widget ID to get parent and child
                int parentId = widgetId >> 16;
                int childId = widgetId & 0xFFFF;
                data.addProperty("parentWidgetId", parentId);
                data.addProperty("childWidgetId", childId);
            }
            else
            {
                data.addProperty("hasSelection", false);
                data.addProperty("selectedWidgetId", -1);
                data.addProperty("selectedWidgetName", "");
            }
            
            // Also check for selected spell via VarPlayer (alternative detection method)
            // VarPlayer 276 tracks autocast spell selection in some cases
            int selectedSpellVarp = client.getVarpValue(276);
            data.addProperty("selectedSpellVarp", selectedSpellVarp);
            
            return data;
        });
        
        sendJsonResponse(exchange, selectedData);
    }

    public void handleBank(HttpExchange exchange) throws IOException
    {
        // Parse query parameters: /bank?itemId=995
        String query = exchange.getRequestURI().getQuery();
        Integer targetItemId = null;
        
        if (query != null)
        {
            Map<String, String> params = new java.util.HashMap<>();
            for (String param : query.split("&"))
            {
                String[] pair = param.split("=");
                if (pair.length == 2)
                {
                    params.put(pair[0], pair[1]);
                }
            }
            
            if (params.containsKey("itemId"))
            {
                try
                {
                    targetItemId = Integer.parseInt(params.get("itemId"));
                }
                catch (NumberFormatException ex)
                {
                    exchange.sendResponseHeaders(400, 0);
                    exchange.getResponseBody().close();
                    return;
                }
            }
        }
        
        final Integer itemIdParam = targetItemId;
        
        Object bankData = invokeAndWait(() -> {
            ItemContainer bankContainer = client.getItemContainer(InventoryID.BANK);
            if (bankContainer == null) return null;

            Item[] bankItems = bankContainer.getItems();
            
            // If itemId parameter is provided, search for that item and return its data
            if (itemIdParam != null)
            {
                // Search for the item in the bank
                int foundSlot = -1;
                for (int i = 0; i < bankItems.length; i++)
                {
                    if (bankItems[i].getId() == itemIdParam)
                    {
                        foundSlot = i;
                        break;
                    }
                }
                
                if (foundSlot == -1)
                {
                    // Item not found in bank
                    return null;
                }
                
                Item item = bankItems[foundSlot];
                JsonObject itemData = new JsonObject();
                itemData.addProperty("slot", foundSlot);
                itemData.addProperty("id", item.getId());
                itemData.addProperty("quantity", item.getQuantity());
                
                // Get widget data from BankMain.ITEMS children
                Widget bankItemsWidget = client.getWidget(WidgetInfo.BANK_ITEM_CONTAINER);
                if (bankItemsWidget != null)
                {
                    Widget[] children = bankItemsWidget.getChildren();
                    if (children != null && foundSlot < children.length)
                    {
                        Widget slotWidget = children[foundSlot];
                        if (slotWidget != null)
                        {
                            JsonObject widgetData = new JsonObject();
                            widgetData.addProperty("id", slotWidget.getId());
                            widgetData.addProperty("itemId", slotWidget.getItemId());
                            widgetData.addProperty("itemQuantity", slotWidget.getItemQuantity());
                            
                            Point canvasLocation = slotWidget.getCanvasLocation();
                            if (canvasLocation != null)
                            {
                                widgetData.addProperty("x", canvasLocation.getX());
                                widgetData.addProperty("y", canvasLocation.getY());
                            }
                            
                            widgetData.addProperty("width", slotWidget.getWidth());
                            widgetData.addProperty("height", slotWidget.getHeight());
                            boolean isAccessible = (canvasLocation.getY() + slotWidget.getHeight()) < (bankItemsWidget.getCanvasLocation().getY() + bankItemsWidget.getHeight());
                            widgetData.addProperty("accessible", isAccessible);
                            widgetData.addProperty("hidden", slotWidget.isHidden());
                            widgetData.addProperty("name", slotWidget.getName());
                            
                            itemData.add("widget", widgetData);
                        }
                    }
                }
                
                return itemData;
            }
            
            // Otherwise, return all bank items as array
            JsonArray items = new JsonArray();
            for (int i = 0; i < bankItems.length; i++)
            {
                Item item = bankItems[i];
                if (item.getId() == -1) continue;

                JsonObject itemData = new JsonObject();
                itemData.addProperty("slot", i);
                itemData.addProperty("id", item.getId());
                itemData.addProperty("quantity", item.getQuantity());
                items.add(itemData);
            }

            return items;
        });

        if (bankData == null)
        {
            exchange.sendResponseHeaders(204, 0);
            return;
        }

        exchange.sendResponseHeaders(200, 0);
        try (OutputStreamWriter out = new OutputStreamWriter(exchange.getResponseBody()))
        {
            RuneLiteAPI.GSON.toJson(bankData, out);
        }
    }

    private HttpHandler handlerForInv(InventoryID inventoryID)
    {
        return exchange -> {
            Item[] items = invokeAndWait(() -> {
                ItemContainer itemContainer = client.getItemContainer(inventoryID);
                if (itemContainer != null)
                {
                    return itemContainer.getItems();
                }
                return null;
            });

            if (items == null)
            {
                exchange.sendResponseHeaders(204, 0);
                return;
            }

            exchange.sendResponseHeaders(200, 0);
            try (OutputStreamWriter out = new OutputStreamWriter(exchange.getResponseBody()))
            {
                RuneLiteAPI.GSON.toJson(items, out);
            }
        };
    }

    private void sendJsonResponse(HttpExchange exchange, JsonObject data) throws IOException
    {
        if (data == null)
        {
            exchange.sendResponseHeaders(204, 0);
            return;
        }

        exchange.sendResponseHeaders(200, 0);
        try (OutputStreamWriter out = new OutputStreamWriter(exchange.getResponseBody()))
        {
            RuneLiteAPI.GSON.toJson(data, out);
        }
    }

    private <T> T invokeAndWait(Callable<T> r)
    {
        try
        {
            AtomicReference<T> ref = new AtomicReference<>();
            Semaphore semaphore = new Semaphore(0);
            clientThread.invokeLater(() -> {
                try
                {

                    ref.set(r.call());
                }
                catch (Exception e)
                {
                    throw new RuntimeException(e);
                }
                finally
                {
                    semaphore.release();
                }
            });
            semaphore.acquire();
            return ref.get();
        }
        catch (Exception e)
        {
            throw new RuntimeException(e);
        }
    }
}