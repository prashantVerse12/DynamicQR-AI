import FormDefinitionEditor from "./FormDefinitionEditor";
import { createDefaultForm, parseFormContent } from "./formDefinitionUtils";

const CONTENT_TYPES = ["URL", "TEXT", "FORM"];

function ContentEditor({ contentType, content, onTypeChange, onContentChange, disabled = false }) {
  const formContent = contentType === "FORM" ? parseFormContent(content) : null;

  return (
    <div className="space-y-3">
      <label className="block font-semibold">
        Content type
        <select
          className="border p-3 w-full rounded mt-2"
          value={contentType}
          disabled={disabled}
          onChange={(event) => {
            const nextType = event.target.value;
            onTypeChange(nextType);
            if (nextType === "FORM" && !parseFormContent(content)) {
              onContentChange(createDefaultForm());
            }
          }}
        >
          {CONTENT_TYPES.map((type) => <option key={type} value={type}>{type}</option>)}
        </select>
      </label>

      {contentType === "URL" && (
        <label className="block font-semibold">
          Destination URL
          <input
            required
            type="url"
            className="border p-3 w-full rounded mt-2"
            placeholder="https://example.com"
            value={typeof content === "string" ? content : ""}
            disabled={disabled}
            onChange={(event) => onContentChange(event.target.value)}
          />
        </label>
      )}

      {contentType === "TEXT" && (
        <label className="block font-semibold">
          Text content
          <textarea
            required
            maxLength={10000}
            rows={5}
            className="border p-3 w-full rounded mt-2"
            value={typeof content === "string" ? content : ""}
            disabled={disabled}
            onChange={(event) => onContentChange(event.target.value)}
          />
          <span className="block text-sm font-normal text-gray-600">
            {(typeof content === "string" ? content.length : 0)}/10,000 characters
          </span>
        </label>
      )}

      {contentType === "FORM" && (
        formContent ? (
          <FormDefinitionEditor
            value={formContent}
            disabled={disabled}
            onChange={onContentChange}
          />
        ) : (
          <p className="bg-red-100 text-red-800 rounded p-3">
            This form definition is malformed and cannot be edited safely.
          </p>
        )
      )}
    </div>
  );
}

export default ContentEditor;
