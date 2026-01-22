import mouseService from "./services/mouseService";

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

if (require.main === module) {
	demonstrateMouseMovement().catch(console.error);
}
