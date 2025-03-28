import { useState } from "react";
// import TextField from '@mui/material/TextField';

interface CheckboxPropType {
  label: string;
  checked?: boolean;
  disabled?: boolean;
  id?: string;
  name?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

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
