# Sony Alpha 1 - Complete Shutter Speed Value Calculations

Based on Sony SDK documentation:
> The real value of shutter speed (Upper two bytes: numerator, Lower two bytes: denominator)
> In the case of the shutter speed is displayed as "Fraction Number" on the camera, the numerator is fixed 0x0001.
> e.g.) 0x000103E8: 0x0001 (means 1) / 0x03E8 (means 1000) = 1/1000

## Format: 0xNNNNDDDD
- NNNN = Numerator (upper 2 bytes)
- DDDD = Denominator (lower 2 bytes)

## Fraction Shutter Speeds (1/X format)
Numerator = 0x0001, Denominator = X in hex

| Display  | Denominator (Dec) | Denominator (Hex) | SDK Value    |
|----------|-------------------|-------------------|--------------|
| 1/8000   | 8000              | 0x1F40            | 0x00011F40   |
| 1/6400   | 6400              | 0x1900            | 0x00011900   |
| 1/5000   | 5000              | 0x1388            | 0x00011388   |
| 1/4000   | 4000              | 0x0FA0            | 0x00010FA0   |
| 1/3200   | 3200              | 0x0C80            | 0x00010C80   |
| 1/2500   | 2500              | 0x09C4            | 0x000109C4   |
| 1/2000   | 2000              | 0x07D0            | 0x000107D0   |
| 1/1600   | 1600              | 0x0640            | 0x00010640   |
| 1/1250   | 1250              | 0x04E2            | 0x000104E2   |
| 1/1000   | 1000              | 0x03E8            | 0x000103E8   |
| 1/800    | 800               | 0x0320            | 0x00010320   |
| 1/640    | 640               | 0x0280            | 0x00010280   |
| 1/500    | 500               | 0x01F4            | 0x000101F4   |
| 1/400    | 400               | 0x0190            | 0x00010190   |
| 1/320    | 320               | 0x0140            | 0x00010140   |
| 1/250    | 250               | 0x00FA            | 0x000100FA   |
| 1/200    | 200               | 0x00C8            | 0x000100C8   |
| 1/160    | 160               | 0x00A0            | 0x000100A0   |
| 1/125    | 125               | 0x007D            | 0x0001007D   |
| 1/100    | 100               | 0x0064            | 0x00010064   |
| 1/80     | 80                | 0x0050            | 0x00010050   |
| 1/60     | 60                | 0x003C            | 0x0001003C   |
| 1/50     | 50                | 0x0032            | 0x00010032   |
| 1/40     | 40                | 0x0028            | 0x00010028   |
| 1/30     | 30                | 0x001E            | 0x0001001E   |
| 1/25     | 25                | 0x0019            | 0x00010019   |
| 1/20     | 20                | 0x0014            | 0x00010014   |
| 1/15     | 15                | 0x000F            | 0x0001000F   |
| 1/13     | 13                | 0x000D            | 0x0001000D   |
| 1/10     | 10                | 0x000A            | 0x0001000A   |
| 1/8      | 8                 | 0x0008            | 0x00010008   |
| 1/6      | 6                 | 0x0006            | 0x00010006   |
| 1/5      | 5                 | 0x0005            | 0x00010005   |
| 1/4      | 4                 | 0x0004            | 0x00010004   |
| 1/3      | 3                 | 0x0003            | 0x00010003   |

## Long Exposure Shutter Speeds (X.X" format)
Numerator = (display value × 10), Denominator = 0x000A (10)

| Display | Seconds | Numerator (×10) | Numerator (Hex) | SDK Value    |
|---------|---------|-----------------|-----------------|--------------|
| 0.4"    | 0.4     | 4               | 0x0004          | 0x0004000A   |
| 0.5"    | 0.5     | 5               | 0x0005          | 0x0005000A   |
| 0.6"    | 0.6     | 6               | 0x0006          | 0x0006000A   |
| 0.8"    | 0.8     | 8               | 0x0008          | 0x0008000A   |
| 1.0"    | 1.0     | 10              | 0x000A          | 0x000A000A   |
| 1.3"    | 1.3     | 13              | 0x000D          | 0x000D000A   |
| 1.6"    | 1.6     | 16              | 0x0010          | 0x0010000A   |
| 2.0"    | 2.0     | 20              | 0x0014          | 0x0014000A   |
| 2.5"    | 2.5     | 25              | 0x0019          | 0x0019000A   |
| 3.2"    | 3.2     | 32              | 0x0020          | 0x0020000A   |
| 4.0"    | 4.0     | 40              | 0x0028          | 0x0028000A   |
| 5.0"    | 5.0     | 50              | 0x0032          | 0x0032000A   |
| 6.0"    | 6.0     | 60              | 0x003C          | 0x003C000A   |
| 8.0"    | 8.0     | 80              | 0x0050          | 0x0050000A   |
| 10.0"   | 10.0    | 100             | 0x0064          | 0x0064000A   |
| 13.0"   | 13.0    | 130             | 0x0082          | 0x0082000A   |
| 15.0"   | 15.0    | 150             | 0x0096          | 0x0096000A   |
| 20.0"   | 20.0    | 200             | 0x00C8          | 0x00C8000A   |
| 25.0"   | 25.0    | 250             | 0x00FA          | 0x00FA000A   |
| 30.0"   | 30.0    | 300             | 0x012C          | 0x012C000A   |

## BULB Mode
BULB is typically represented as 0x00000000 or a special constant.

---

## ⚠️ CRITICAL DISCOVERY CONFLICT

**We previously tested and CONFIRMED these values work:**
- 1/8000 = **0x00010001** ✓ (tested working)
- 1/250 = **0x00010006** ✓ (tested working)
- 1/60 = **0x00010008** ✓ (tested working)

**But documentation says:**
- 1/8000 should be **0x00011F40**
- 1/250 should be **0x000100FA**
- 1/60 should be **0x0001003C**

**This means we have TWO different encoding systems:**

### System A: Sequential Index (0x00010001, 0x00010002...)
- Used for SET operations
- Confirmed working in our tests
- NOT in documentation

### System B: Numerator/Denominator (0x00011F40, 0x000103E8...)
- Documented in Sony SDK manual
- Mathematically correct representation
- Untested on our camera

---

## 🧪 Next Step: Test Both Formats

We need to determine which format the camera actually uses:

1. **Keep System A** (sequential) - currently working
2. **Try System B** (documented) - see if it also works or works better
3. **Document which format is correct** for Sony Alpha 1

**Hypothesis:** Sony SDK might accept BOTH formats, or different cameras use different formats.
