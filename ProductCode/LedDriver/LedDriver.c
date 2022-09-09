/* Vector Cast デモ用のコード: デバッグ前 */

#include "LedDriver.h"

/* Led module を初期化 */
void LedDriver_Init(stc_led_t* self, uint8_t* pLedOutputReg)
{
    self->pLedOutputReg = pLedOutputReg;
}

/* Led をすべて点灯する */
void LedDriver_LedAllOn(stc_led_t* self)
{
    if(self->pLedOutputReg == NULL)
    {
        return;
    }

    *(self->pLedOutputReg) = 0xFFu;
}

/* "ledIdx" により指定されたLED を点灯する */
void LedDriver_LedOn(stc_led_t* self, int ledIdx)
{
    if(self->pLedOutputReg == NULL)
    {
        return;
    }

    if((ledIdx < 1) || (8 < ledIdx))
    {
        return;
    }

    *(self->pLedOutputReg) |= (1u << ledIdx);
}

/* LEDをすべて消灯する */
void LedDriver_LedAllOff(stc_led_t* self)
{
    if(self->pLedOutputReg == NULL)
    {
        return;
    }

    *(self->pLedOutputReg) = 0x0u;
}

/* "ledIdx"により指定されたLEDを消灯する */
void LedDriver_LedOff(stc_led_t* self, int ledIdx)
{
    if(self->pLedOutputReg == NULL)
    {
        return;
    }

    if((ledIdx < 1) || (8 < ledIdx))
    {
        return;
    }

    *(self->pLedOutputReg) &= ~(1u << ledIdx);
}


