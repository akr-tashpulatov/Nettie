'use client';

import * as React from 'react';
import { useHookFormMask } from 'use-mask-input';
import { Input } from './input';
import { PHONE_MASK_CONFIG } from '../constants/masks';

interface PhoneInputProps {
  registerWithMask: ReturnType<typeof useHookFormMask>;
  name: string;
  placeholder?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  className?: string;
}

export function PhoneInput({
  registerWithMask,
  name,
  placeholder,
  leftIcon,
  rightIcon,
  className,
}: PhoneInputProps) {
  return (
    <Input
      type="tel"
      placeholder={placeholder}
      leftIcon={leftIcon}
      rightIcon={rightIcon}
      className={className}
      {...registerWithMask(name, PHONE_MASK_CONFIG.mask, {
        required: true,
        setValueAs: PHONE_MASK_CONFIG.transform,
      })}
    />
  );
}
