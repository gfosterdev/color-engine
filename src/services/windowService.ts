import { getWindows } from "@nut-tree-fork/nut-js";

export interface WindowInfo {
	title: string;
	x: number;
	y: number;
	width: number;
	height: number;
}

export class WindowService {
	/**
	 * Finds a window by its title (case-insensitive partial match)
	 * @param title - The window title or partial title to search for
	 * @returns WindowInfo object with window position and dimensions, or null if not found
	 */
	async findWindowByTitle(title: string): Promise<WindowInfo | null> {
		try {
			const windows = await getWindows();

			// Find window with matching title (case-insensitive)
			for (const window of windows) {
				const windowTitle = await window.title;
				if (windowTitle.toLowerCase().includes(title.toLowerCase())) {
					const region = await window.region;

					return {
						title: windowTitle,
						x: region.left,
						y: region.top,
						width: region.width,
						height: region.height,
					};
				}
			}

			return null;
		} catch (error) {
			console.error("Error finding window:", error);
			return null;
		}
	}
}
