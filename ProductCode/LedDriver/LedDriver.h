#ifndef _LEDDRIVER_H_
#define _LEDDRIVER_H_

#include "stdint.h"

/* LED module を表す構造体 */
typedef struct
{
    uint8_t* pLedOutputReg; /* LED output register のアドレスへのポインタ */
} stc_led_t;

void LedDriver_Init(stc_led_t* self, uint8_t* pLedOutputReg);
void LedDriver_LedAllOn(stc_led_t* self);
void LedDriver_LedOn(stc_led_t* self, int ledIdx);
void LedDriver_LedAllOff(stc_led_t* self);
void LedDriver_LedOff(stc_led_t* self, int ledIdx);

#endif
