import { useState } from "react";
// import TextField from '@mui/material/TextField';

interface CheckboxPropType {
  label: string;
  checked?: boolean;
  disabled?: boolean;
  id?: string;
  name?: string;
  onChange?: (value: boolean) => void;
}

const Checkbox = ({
  label,
  checked = false,
  disabled = false,
  onChange = undefined,
  name = "",
  id = "",
}: CheckboxPropType) => {
  const [isChecked, setIsChecked] = useState<boolean>(checked);
  const handleChange = () => {
    setIsChecked(!isChecked);
    if (onChange) {
      onChange(!isChecked);
    }
  };
  return (
    <div
      className="block flex justify-start items-center mb-1 cursor-pointer"
      onClick={handleChange}
    >
      <input
        type="checkbox"
        checked={isChecked}
        name={name}
        id={id}
        readOnly
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
