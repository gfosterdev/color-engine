import mouseService from "./services/mouseService";
import windowService from "./services/windowService";

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

if (require.main === module) {
	// Run window identification demo by default
	demonstrateWindowIdentification().catch(console.error);

	// Uncomment to run mouse demo instead:
	// demonstrateMouseMovement().catch(console.error);
}
