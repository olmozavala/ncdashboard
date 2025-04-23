/**
 * Button Component
 * 
 * A reusable button component that provides consistent styling and behavior
 * across the application. Supports loading states, disabled states, and custom
 * styling through additional classes.
 * 
 * @component
 * @example
 * ```tsx
 * <Button
 *   text="Click Me"
 *   onClick={() => console.log('clicked')}
 *   disabled={false}
 *   loading={false}
 *   additionalClasses="w-full"
 * />
 * ```
 */

/**
 * Props interface for the Button component
 * 
 * @interface ButtonProps
 * @property {string} text - The text to display on the button
 * @property {() => void} onClick - Callback function when button is clicked
 * @property {boolean} [disabled=false] - Whether the button is disabled
 * @property {boolean} [loading=false] - Whether the button is in loading state
 * @property {string} [additionalClasses=''] - Additional CSS classes to apply
 */
interface ButtonProps {
    /** The text to display on the button */
    text: string;
    /** Callback function when button is clicked */
    onClick: () => void;
    /** Whether the button is disabled */
    disabled?: boolean;
    /** Whether the button is in loading state */
    loading?: boolean;
    /** Additional CSS classes to apply */
    additionalClasses?: string;
}

/**
 * Button Component
 * 
 * @param {ButtonProps} props - The props for the button component
 * @returns {JSX.Element} A styled button element
 */
const Button = (props: ButtonProps) => {
    return (
        <button
            className={`bg-nc-100 hover:bg-nc-200 text-white py-2 px-4 rounded ${
                props.disabled ? 'opacity-50 cursor-not-allowed' : ''
            } ${props.additionalClasses}`}
            onClick={props.onClick}
            disabled={props.disabled}
        >
            {props.loading ? 'Loading...' : props.text}
        </button>
    )
}

export default Button