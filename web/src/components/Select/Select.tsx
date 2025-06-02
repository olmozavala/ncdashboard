/**
 * Select Component
 * 
 * A reusable select (dropdown) component that provides consistent styling and behavior
 * across the application. Supports disabled state, loading state, and custom
 * styling through additional classes.
 * 
 * @component
 * @example
 * ```tsx
 * <Select
 *   options={[{ label: 'Option 1', value: '1' }, { label: 'Option 2', value: '2' }]}
 *   value={selectedValue}
 *   onChange={val => setSelectedValue(val)}
 *   disabled={false}
 *   loading={false}
 *   additionalClasses="w-full"
 * />
 * ```
 */

/**
 * Option interface for the Select component
 * @interface SelectOption
 * @property {string} label - The display label for the option
 * @property {string} value - The value for the option
 */
interface SelectOption {
    label: string;
    value: string;
}

/**
 * Props interface for the Select component
 * @interface SelectProps
 * @property {SelectOption[]} options - The options to display in the dropdown
 * @property {string} value - The currently selected value
 * @property {(value: string) => void} onChange - Callback when selection changes
 * @property {boolean} [disabled=false] - Whether the select is disabled
 * @property {boolean} [loading=false] - Whether the select is in loading state
 * @property {string} [additionalClasses=''] - Additional CSS classes to apply
 */
interface SelectProps {
    options: SelectOption[];
    value: string;
    onChange: (value: string) => void;
    disabled?: boolean;
    loading?: boolean;
    additionalClasses?: string;
}

/**
 * Select Component
 * 
 * @param {SelectProps} props - The props for the select component
 * @returns {JSX.Element} A styled select element
 */
const Select = (props: SelectProps) => {
    return (
        <select
            className={`bg-nc-100 hover:bg-nc-200 text-white py px-4 rounded ${
                props.disabled ? 'opacity-50 cursor-not-allowed' : ''
            } ${props.additionalClasses}`}
            value={props.value}
            onChange={e => props.onChange(e.target.value)}
            disabled={props.disabled || props.loading}
        >
            {props.loading ? (
                <option>Loading...</option>
            ) : (
                props.options.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))
            )}
        </select>
    )
}

export default Select
