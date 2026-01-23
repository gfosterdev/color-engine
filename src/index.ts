import mouseService from "./services/mouseService";
import windowService from "./services/windowService";
import runeliteService from "./services/runeliteService";

async function demonstrateMouseMovement() {
	console.log("Moving mouse to (100, 100)...");
	await mouseService.moveTo(100, 100);
	await new Promise((resolve) => setTimeout(resolve, 1000));

	console.log("Moving mouse to (500, 300)...");
	await mouseService.moveTo(500, 300);
	await new Promise((resolve) => setTimeout(resolve, 1000));

	console.log("Moving mouse to (800, 600)...");
	await mouseService.moveTo(800, 600);

	console.log("Mouse demonstration complete!");
}

async function demonstrateWindowIdentification() {
	console.log("\n=== Window Identification Demo ===\n");

	// Example: Find a specific window (e.g., Chrome, VSCode, etc.)
	console.log("Looking for a runelite...");
	const runelite = await windowService.findWindowByTitle(
		"RuneLite - George GIM",
	);
	if (runelite) {
		const center = windowService.getWindowCenter(runelite);
		console.log(`Center point: (${center.x}, ${center.y})`);

		// Example: Move mouse to window center
		console.log("\nMoving mouse to runelite window center...");
		await mouseService.moveTo(center.x, center.y);
		await new Promise((resolve) => setTimeout(resolve, 1000));

		// Example: Move to a point relative to window (50, 50 from top-left)
		const relativePoint = windowService.relativeToAbsolute(
			runelite,
			50,
			50,
		);
		console.log(
			`Moving to relative point (50, 50) = absolute (${relativePoint.x}, ${relativePoint.y})...`,
		);
		await mouseService.moveTo(relativePoint.x, relativePoint.y);
	} else {
		console.log(
			"No runelite window found. Try searching for another application!",
		);
	}

	console.log("\nWindow identification demo complete!");
}

async function demonstrateRuneLiteService() {
	console.log("\n=== RuneLite Service Demo ===\n");

	// Find the RuneLite window
	console.log("Finding RuneLite window...");
	const window = await runeliteService.findWindow();

	if (!window) {
		console.log(
			"RuneLite window not found! Make sure RuneLite is running.",
		);
		return;
	}

	console.log(`Found: "${window.title}"`);

	// Get window info
	const dimensions = await runeliteService.getWindowDimensions();
	const position = await runeliteService.getWindowPosition();
	console.log(`Position: (${position?.x}, ${position?.y})`);
	console.log(`Size: ${dimensions?.width}x${dimensions?.height}\n`);

	// Move to specific relative coordinates
	console.log("Moving to (100, 100) relative to window...");
	await runeliteService.moveToRelative(100, 100);
	await new Promise((resolve) => setTimeout(resolve, 800));

	// Move using percentages
	console.log("Moving to 50%, 50% of window (center-ish)...");
	await runeliteService.moveToPercent(50, 50);
	await new Promise((resolve) => setTimeout(resolve, 800));

	// Move to specific coordinates
	console.log("Moving to (200, 150) relative to window...");
	await runeliteService.moveToRelative(200, 150);
	await new Promise((resolve) => setTimeout(resolve, 800));

	// Move to another position
	console.log("Moving to (300, 250) relative to window...");
	await runeliteService.moveToRelative(300, 250);
	await new Promise((resolve) => setTimeout(resolve, 800));

	// Get current relative mouse position
	const relativePos = await runeliteService.getRelativeMousePosition();
	if (relativePos) {
		console.log(
			`\nCurrent relative mouse position: (${relativePos.x}, ${relativePos.y})`,
		);
	}

	// Check if mouse is in window
	const isInWindow = await runeliteService.isMouseInWindow();
	console.log(`Mouse is in RuneLite window: ${isInWindow}`);

	console.log("\nRuneLite service demo complete!");
}

if (require.main === module) {
	// Run RuneLite service demo by default
	demonstrateRuneLiteService().catch(console.error);

	// Uncomment to run other demos:
	// demonstrateWindowIdentification().catch(console.error);
	// demonstrateMouseMovement().catch(console.error);
}
