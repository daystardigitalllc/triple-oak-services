import ImageComponent from "./astro-assets-image.astro";
export { ImageComponent as Image };

export async function getImage(options: any) {
  return {
    src: typeof options.src === 'object' && options.src !== null ? options.src.src : options.src,
    attributes: {}
  };
}
