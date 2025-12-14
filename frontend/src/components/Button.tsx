import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'subtle';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  fullWidth?: boolean;
  children: React.ReactNode;
}

const Spinner = () => (
  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
  </svg>
);

const VARIANT_CLASSES = {
  primary: 'bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800 focus-visible:ring-primary-500 shadow-sm',
  secondary: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 active:bg-gray-100 focus-visible:ring-gray-400',
  success: 'bg-green-600 text-white hover:bg-green-700 active:bg-green-800 focus-visible:ring-green-500 shadow-sm',
  danger: 'bg-red-600 text-white hover:bg-red-700 active:bg-red-800 focus-visible:ring-red-500 shadow-sm',
  subtle: 'bg-gray-100 text-gray-700 hover:bg-gray-200 active:bg-gray-300 focus-visible:ring-gray-400',
};

const SIZE_CLASSES = {
  sm: 'px-3 py-2 text-xs min-h-[32px]',
  md: 'px-4 py-2.5 text-sm min-h-[40px]',
  lg: 'px-6 py-3 text-base min-h-[48px]',
};

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  fullWidth = false,
  children,
  disabled,
  className = '',
  ...props
}) => {
  return (
    <button
      className={`
        inline-flex items-center justify-center gap-2 font-medium rounded-lg 
        transition-all duration-150 
        focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 
        disabled:opacity-50 disabled:cursor-not-allowed
        active:scale-[0.98]
        touch-manipulation
        select-none
        ${VARIANT_CLASSES[variant]}
        ${SIZE_CLASSES[size]}
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && <Spinner />}
      {children}
    </button>
  );
};

// Convenience exports
export const PrimaryButton: React.FC<Omit<ButtonProps, 'variant'>> = (props) => (
  <Button variant="primary" {...props} />
);

export const SecondaryButton: React.FC<Omit<ButtonProps, 'variant'>> = (props) => (
  <Button variant="secondary" {...props} />
);

export const SuccessButton: React.FC<Omit<ButtonProps, 'variant'>> = (props) => (
  <Button variant="success" {...props} />
);

export const DangerButton: React.FC<Omit<ButtonProps, 'variant'>> = (props) => (
  <Button variant="danger" {...props} />
);
