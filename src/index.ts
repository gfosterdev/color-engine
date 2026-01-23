import { WindowService } from "./services/windowService";

if (require.main === module) {
	(async () => {
		const windowService = new WindowService();
		const window = await windowService.findWindowByTitle(
			"RuneLite - George GIM",
		);
		console.log(window);
		await windowService.moveMouseToWindowPosition(100, 100);
		// await windowService.captureWindow("runeLiteWindow");
	})();
}
