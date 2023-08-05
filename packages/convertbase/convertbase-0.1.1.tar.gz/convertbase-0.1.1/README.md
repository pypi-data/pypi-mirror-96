Universal base converter

Use either with predefined converters:
 - integer to base32(RFC4648)
 - integer to hex
 - base32(RFC4648) to integer

Or use with custom settings:
- set base
- set charset


    #Examples:
    if __name__ == "__main__":
        # example:
        num = 15851

        # using instance of converter, using custom settings
        converter = Convertbase()
        converter.set_base(32)
        converter.set_charset('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567')

        print(converter.convert(num))

        # or using static methods:
        print(Convertbase.to_b32(num))
        print(hex(num))

        #convert back:
        print(Convertbase.from_b32_to_dec('PPL'))
