/**
 * CheckBox Component
 * 
 * A reusable checkbox component that provides consistent styling and behavior
 * across the application. Supports disabled states, labels, and custom styling.
 * 
 * @component
 * @example
 * ```tsx
 * <CheckBox
 *   label="Enable Feature"
 *   checked={true}
 *   disabled={false}
 *   onChange={(e) => console.log(e.target.checked)}
 *   name="feature"
 *   id="feature-checkbox"
 * />
 * ```
 */

/**
 * Props interface for the CheckBox component
 * 
 * @interface CheckboxPropType
 * @property {string} label - The text label for the checkbox
 * @property {boolean} [checked=false] - Whether the checkbox is checked
 * @property {boolean} [disabled=false] - Whether the checkbox is disabled
 * @property {string} [id=''] - Unique identifier for the checkbox
 * @property {string} [name=''] - Name attribute for form submission
 * @property {(e: React.ChangeEvent<HTMLInputElement>) => void} [onChange] - Callback when checkbox state changes
 */
interface CheckboxPropType {
  /** The text label for the checkbox */
  label: string;
  /** Whether the checkbox is checked */
  checked?: boolean;
  /** Whether the checkbox is disabled */
  disabled?: boolean;
  /** Unique identifier for the checkbox */
  id?: string;
  /** Name attribute for form submission */
  name?: string;
  /** Callback when checkbox state changes */
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

/**
 * CheckBox Component
 * 
 * @param {CheckboxPropType} props - The props for the checkbox component
 * @returns {JSX.Element} A styled checkbox input with label
 */
const Checkbox = ({
  label,
  checked = false,
  disabled = false,
  onChange = undefined,
  name = "",
  id = "",
}: CheckboxPropType) => {

  return (
    <div
      className="block flex justify-start items-center mb-1 cursor-pointer"
    >
      <input
        type="checkbox"
        checked={checked}
        name={name}
        id={id}
        onChange={onChange}
        style={
          disabled
            ? { backgroundColor: "rgb(156 163 175)", cursor: "not-allowed" }
            : {}
        }
        className="cursor-pointer rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-300 focus:ring focus:ring-offset-0 focus:ring-indigo-200 focus:ring-opacity-50"
      />
      <label
        htmlFor={id}
        className="cursor-pointer text-base ml-2"
        style={disabled ? { cursor: "not-allowed" } : {}}
      >
        {label}
      </label>
    </div>
  );
};

export default Checkbox;
