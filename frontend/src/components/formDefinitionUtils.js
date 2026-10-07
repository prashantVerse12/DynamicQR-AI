export const DEFAULT_FIELD = {
  name: "field_1",
  label: "Field 1",
  type: "text",
  required: false,
  max_length: 255,
};

export const createDefaultForm = () => ({
  title: "",
  fields: [{ ...DEFAULT_FIELD }],
  submit_label: "Submit",
});

export function parseFormContent(content) {
  if (typeof content === "object" && content !== null) return content;
  if (typeof content !== "string") return null;

  try {
    const parsed = JSON.parse(content);
    return parsed && typeof parsed === "object" ? parsed : null;
  } catch {
    return null;
  }
}
