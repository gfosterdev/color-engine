package net.runelite.client.plugins.httpserver;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.net.InetSocketAddress;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.Semaphore;
import java.util.concurrent.atomic.AtomicReference;
import javax.inject.Inject;
import net.runelite.api.*;
import net.runelite.api.coords.LocalPoint;
import net.runelite.api.coords.Point;
import net.runelite.api.coords.WorldPoint;
import net.runelite.api.widgets.Widget;
import net.runelite.api.widgets.WidgetInfo;
import net.runelite.api.Perspective;
import net.runelite.client.callback.ClientThread;
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
        server.createContext("/equip", handlerForInv(InventoryID.EQUIPMENT));
        server.createContext("/bank", this::handleBank);

        // World data
        server.createContext("/npcs", this::handleNPCs);
        server.createContext("/players", this::handlePlayers);
        server.createContext("/objects", this::handleObjects);
        server.createContext("/grounditems", this::handleGroundItems);
        server.createContext("/npcs_in_viewport", this::getNPCsInViewport);

        // Game state
        server.createContext("/camera", this::handleCamera);
        server.createContext("/game", this::handleGameState);
        server.createContext("/menu", this::handleMenu);
        server.createContext("/widgets", this::handleWidgets);

        server.setExecutor(Executors.newSingleThreadExecutor());
        server.start();
    }

    @Override
    protected void shutDown() throws Exception
    {
        server.stop(1);
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

    public void getNPCsInViewport(HttpExchange exchange) throws IOException
    {
        JsonArray npcsData = invokeAndWait(() -> {
            JsonArray npcs = new JsonArray();
            List<NPC> npcList = client.getNpcs();

            for (NPC npc : npcList)
            {
                if (npc == null) continue;

                WorldPoint wp = npc.getWorldLocation();
                LocalPoint lp = npc.getLocalLocation();
                Point point = Perspective.localToCanvas(client, lp, wp.getPlane());
                if (point != null)
                {
                    JsonObject npcData = new JsonObject();
                    npcData.addProperty("name", npc.getName());
                    npcData.addProperty("id", npc.getId());
                    npcData.addProperty("x", point.getX());
                    npcData.addProperty("y", point.getY());
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
            data.addProperty("x", client.getCameraX());
            data.addProperty("y", client.getCameraY());
            data.addProperty("z", client.getCameraZ());

            return data;
        });

        sendJsonResponse(exchange, cameraData);
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
        JsonArray menuData = invokeAndWait(() -> {
            JsonArray menu = new JsonArray();
            MenuEntry[] entries = client.getMenuEntries();

            for (MenuEntry entry : entries)
            {
                JsonObject menuEntry = new JsonObject();
                menuEntry.addProperty("option", entry.getOption());
                menuEntry.addProperty("target", entry.getTarget());
                menuEntry.addProperty("type", entry.getType().toString());
                menu.add(menuEntry);
            }

            return menu;
        });

        exchange.sendResponseHeaders(200, 0);
        try (OutputStreamWriter out = new OutputStreamWriter(exchange.getResponseBody()))
        {
            RuneLiteAPI.GSON.toJson(menuData, out);
        }
    }

    public void handleWidgets(HttpExchange exchange) throws IOException
    {
        JsonObject widgetsData = invokeAndWait(() -> {
            JsonObject data = new JsonObject();

            // Check common interfaces
            data.addProperty("isBankOpen", client.getWidget(WidgetInfo.BANK_CONTAINER) != null);
            data.addProperty("isInventoryOpen", !Objects.requireNonNull(client.getWidget(WidgetInfo.INVENTORY)).isHidden());
            data.addProperty("isLogoutPanelOpen", !Objects.requireNonNull(client.getWidget(WidgetInfo.LOGOUT_PANEL)).isHidden());

            // Shop and dialogue detection removed due to API incompatibility
            data.addProperty("isShopOpen", false);
            data.addProperty("isDialogueOpen", false);

            return data;
        });

        sendJsonResponse(exchange, widgetsData);
    }

    public void handleBank(HttpExchange exchange) throws IOException
    {
        JsonArray bankData = invokeAndWait(() -> {
            ItemContainer bankContainer = client.getItemContainer(InventoryID.BANK);
            if (bankContainer == null) return null;

            JsonArray items = new JsonArray();
            Item[] bankItems = bankContainer.getItems();

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