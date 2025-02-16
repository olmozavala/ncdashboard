
interface ButtonProps {
    text: string;
    onClick: () => void;
    disabled?: boolean;
    loading?: boolean;
    additionalClasses?: string;
}

const Button = (props: ButtonProps) => {
    return (
        <button
            className={`bg-nc-100 hover:bg-nc-200 text-white py-2 px-4 rounded ${props.disabled ? 'opacity-50 cursor-not-allowed' : ''} ${props.additionalClasses}`}
            onClick={props.onClick}
            disabled={props.disabled}
        >
            {props.loading ? 'Loading...' : props.text}
        </button>
    )
}

export default Button