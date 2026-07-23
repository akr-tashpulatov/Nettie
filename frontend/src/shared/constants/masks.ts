export const PHONE_MASK_CONFIG = {
  mask: ['+7 (999) 999-99-99'],
  transform: (value: string) => {
    const digitsOnly = value.replace(/\D/g, '');
    return `+${digitsOnly}`;
  },
};
