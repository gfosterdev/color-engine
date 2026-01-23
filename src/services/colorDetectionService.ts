import { Image } from "@nut-tree-fork/nut-js";

export interface RGB {
	r: number;
	g: number;
	b: number;
}

export interface ColorMatch {
	x: number;
	y: number;
	color: RGB;
}

export interface ColorSearchOptions {
	tolerance?: number; // Color tolerance (0-255), default 0 for exact match
	maxResults?: number; // Maximum number of results to return
	region?: {
		// Search within a specific region
		x: number;
		y: number;
		width: number;
		height: number;
	};
}

/**
 * Service for detecting colors in images
 */
class ColorDetectionService {
	/**
	 * Check if two colors match within tolerance
	 */
	private colorMatches(
		color1: RGB,
		color2: RGB,
		tolerance: number = 0,
	): boolean {
		return (
			Math.abs(color1.r - color2.r) <= tolerance &&
			Math.abs(color1.g - color2.g) <= tolerance &&
			Math.abs(color1.b - color2.b) <= tolerance
		);
	}

	/**
	 * Get the color of a pixel at specific coordinates
	 */
	async getColorAt(image: Image, x: number, y: number): Promise<RGB> {
		const width = await image.width;
		const height = await image.height;
		const data = await image.data;

		// Calculate pixel position in RGBA buffer (4 bytes per pixel)
		const index = (y * width + x) * 4;

		return {
			r: data[index],
			g: data[index + 1],
			b: data[index + 2],
		};
	}

	/**
	 * Find all pixels matching a specific color
	 */
	async findColor(
		image: Image,
		targetColor: RGB,
		options: ColorSearchOptions = {},
	): Promise<ColorMatch[]> {
		const { tolerance = 0, maxResults, region } = options;
		const matches: ColorMatch[] = [];

		const width = await image.width;
		const height = await image.height;

		// Determine search boundaries
		const startX = region?.x ?? 0;
		const startY = region?.y ?? 0;
		const endX = region ? Math.min(startX + region.width, width) : width;
		const endY = region ? Math.min(startY + region.height, height) : height;

		// Scan the image
		for (let y = startY; y < endY; y++) {
			for (let x = startX; x < endX; x++) {
				const pixelColor = await this.getColorAt(image, x, y);

				if (this.colorMatches(pixelColor, targetColor, tolerance)) {
					matches.push({ x, y, color: pixelColor });

					// Stop if we've reached max results
					if (maxResults && matches.length >= maxResults) {
						return matches;
					}
				}
			}
		}

		return matches;
	}

	/**
	 * Find the first pixel matching a specific color
	 */
	async findFirstColor(
		image: Image,
		targetColor: RGB,
		options: ColorSearchOptions = {},
	): Promise<ColorMatch | null> {
		const results = await this.findColor(image, targetColor, {
			...options,
			maxResults: 1,
		});
		return results.length > 0 ? results[0] : null;
	}

	/**
	 * Find pixels matching any of the specified colors
	 */
	async findColors(
		image: Image,
		targetColors: RGB[],
		options: ColorSearchOptions = {},
	): Promise<ColorMatch[]> {
		const { tolerance = 0, maxResults, region } = options;
		const matches: ColorMatch[] = [];

		const width = await image.width;
		const height = await image.height;

		const startX = region?.x ?? 0;
		const startY = region?.y ?? 0;
		const endX = region ? Math.min(startX + region.width, width) : width;
		const endY = region ? Math.min(startY + region.height, height) : height;

		for (let y = startY; y < endY; y++) {
			for (let x = startX; x < endX; x++) {
				const pixelColor = await this.getColorAt(image, x, y);

				// Check if pixel matches any target color
				const matchesAnyColor = targetColors.some((targetColor) =>
					this.colorMatches(pixelColor, targetColor, tolerance),
				);

				if (matchesAnyColor) {
					matches.push({ x, y, color: pixelColor });

					if (maxResults && matches.length >= maxResults) {
						return matches;
					}
				}
			}
		}

		return matches;
	}

	/**
	 * Find pixels within a color range
	 */
	async findColorRange(
		image: Image,
		minColor: RGB,
		maxColor: RGB,
		options: ColorSearchOptions = {},
	): Promise<ColorMatch[]> {
		const { maxResults, region } = options;
		const matches: ColorMatch[] = [];

		const width = await image.width;
		const height = await image.height;

		const startX = region?.x ?? 0;
		const startY = region?.y ?? 0;
		const endX = region ? Math.min(startX + region.width, width) : width;
		const endY = region ? Math.min(startY + region.height, height) : height;

		for (let y = startY; y < endY; y++) {
			for (let x = startX; x < endX; x++) {
				const pixelColor = await this.getColorAt(image, x, y);

				// Check if pixel is within range
				const inRange =
					pixelColor.r >= minColor.r &&
					pixelColor.r <= maxColor.r &&
					pixelColor.g >= minColor.g &&
					pixelColor.g <= maxColor.g &&
					pixelColor.b >= minColor.b &&
					pixelColor.b <= maxColor.b;

				if (inRange) {
					matches.push({ x, y, color: pixelColor });

					if (maxResults && matches.length >= maxResults) {
						return matches;
					}
				}
			}
		}

		return matches;
	}

	/**
	 * Count pixels matching a specific color
	 */
	async countColor(
		image: Image,
		targetColor: RGB,
		options: ColorSearchOptions = {},
	): Promise<number> {
		const matches = await this.findColor(image, targetColor, options);
		return matches.length;
	}

	/**
	 * Check if a color exists in the image
	 */
	async hasColor(
		image: Image,
		targetColor: RGB,
		options: ColorSearchOptions = {},
	): Promise<boolean> {
		const match = await this.findFirstColor(image, targetColor, options);
		return match !== null;
	}

	/**
	 * Get the average color of an image or region
	 */
	async getAverageColor(
		image: Image,
		region?: { x: number; y: number; width: number; height: number },
	): Promise<RGB> {
		const width = await image.width;
		const height = await image.height;

		const startX = region?.x ?? 0;
		const startY = region?.y ?? 0;
		const endX = region ? Math.min(startX + region.width, width) : width;
		const endY = region ? Math.min(startY + region.height, height) : height;

		let totalR = 0;
		let totalG = 0;
		let totalB = 0;
		let count = 0;

		for (let y = startY; y < endY; y++) {
			for (let x = startX; x < endX; x++) {
				const pixelColor = await this.getColorAt(image, x, y);
				totalR += pixelColor.r;
				totalG += pixelColor.g;
				totalB += pixelColor.b;
				count++;
			}
		}

		return {
			r: Math.round(totalR / count),
			g: Math.round(totalG / count),
			b: Math.round(totalB / count),
		};
	}
}

export default new ColorDetectionService();
