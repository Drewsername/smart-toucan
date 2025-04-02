export function cn(...inputs: (string | undefined | boolean)[]) {
  return inputs
    .filter(Boolean)
    .join(" ")
    .trim();
}