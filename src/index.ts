import { WindowService } from "./services/windowService";

if (require.main === module) {
	(async () => {
		const windowService = new WindowService();
		const window = await windowService.findWindowByTitle(
			"RuneLite - George GIM",
		);
		console.log(window);
		// await windowService.moveMouseToWindowPosition(100, 100);
		await windowService.captureWindowToMemory(true);
		const matches = await windowService.findColourInCapture(
			{
				r: 220,
				g: 224,
				b: 28,
			},
			20,
		);
		console.log(matches);
		// await windowService.captureWindow("runeLiteWindow");
	})();
}
