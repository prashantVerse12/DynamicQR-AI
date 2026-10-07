import { DEFAULT_FIELD, createDefaultForm } from "./formDefinitionUtils";

const FIELD_TYPES = ["text", "email", "textarea"];

function FormDefinitionEditor({ value, onChange, disabled = false }) {
  const form = value || createDefaultForm();
  const fields = Array.isArray(form.fields) ? form.fields : [];

  const updateForm = (changes) => onChange({ ...form, ...changes });

  const updateField = (index, changes) => {
    const nextFields = fields.map((field, fieldIndex) =>
      fieldIndex === index ? { ...field, ...changes } : field,
    );
    updateForm({ fields: nextFields });
  };

  const addField = () => {
    if (fields.length >= 20) return;
    const nextNumber = fields.length + 1;
    updateForm({
      fields: [
        ...fields,
        {
          ...DEFAULT_FIELD,
          name: `field_${nextNumber}`,
          label: `Field ${nextNumber}`,
        },
      ],
    });
  };

  const removeField = (index) => {
    if (fields.length <= 1) return;
    updateForm({ fields: fields.filter((_, fieldIndex) => fieldIndex !== index) });
  };

  return (
    <div className="space-y-4">
      <label className="block font-semibold">
        Form title
        <input
          className="border p-3 w-full rounded mt-2"
          maxLength={200}
          value={form.title || ""}
          disabled={disabled}
          onChange={(event) => updateForm({ title: event.target.value })}
        />
      </label>
      <label className="block font-semibold">
        Submit label
        <input
          className="border p-3 w-full rounded mt-2"
          maxLength={200}
          value={form.submit_label || ""}
          disabled={disabled}
          onChange={(event) => updateForm({ submit_label: event.target.value })}
        />
      </label>
      <div className="space-y-3">
        {fields.map((field, index) => (
          <fieldset key={`${field.name || "field"}-${index}`} className="border rounded p-3">
            <legend className="px-1 font-semibold">Field {index + 1}</legend>
            <div className="grid gap-3 sm:grid-cols-2">
              <label>
                Name
                <input
                  className="border p-2 w-full rounded mt-1"
                  maxLength={64}
                  value={field.name || ""}
                  disabled={disabled}
                  onChange={(event) => updateField(index, { name: event.target.value })}
                />
              </label>
              <label>
                Label
                <input
                  className="border p-2 w-full rounded mt-1"
                  maxLength={200}
                  value={field.label || ""}
                  disabled={disabled}
                  onChange={(event) => updateField(index, { label: event.target.value })}
                />
              </label>
              <label>
                Type
                <select
                  className="border p-2 w-full rounded mt-1"
                  value={field.type || "text"}
                  disabled={disabled}
                  onChange={(event) => updateField(index, { type: event.target.value })}
                >
                  {FIELD_TYPES.map((type) => <option key={type} value={type}>{type}</option>)}
                </select>
              </label>
              <label>
                Maximum length
                <input
                  type="number"
                  min="1"
                  max="10000"
                  className="border p-2 w-full rounded mt-1"
                  value={field.max_length ?? 255}
                  disabled={disabled}
                  onChange={(event) => updateField(index, { max_length: Number(event.target.value) })}
                />
              </label>
            </div>
            <div className="flex justify-between items-center mt-3">
              <label className="flex gap-2 items-center">
                <input
                  type="checkbox"
                  checked={Boolean(field.required)}
                  disabled={disabled}
                  onChange={(event) => updateField(index, { required: event.target.checked })}
                />
                Required
              </label>
              <button
                type="button"
                className="text-red-700 underline disabled:opacity-50"
                disabled={disabled || fields.length <= 1}
                onClick={() => removeField(index)}
              >
                Remove
              </button>
            </div>
          </fieldset>
        ))}
      </div>
      <button
        type="button"
        className="border border-black px-3 py-2 rounded disabled:opacity-50"
        disabled={disabled || fields.length >= 20}
        onClick={addField}
      >
        Add field ({fields.length}/20)
      </button>
    </div>
  );
}

export default FormDefinitionEditor;
