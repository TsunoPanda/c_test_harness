/* Vector Cast デモ用のコード: デバッグ前 */

#include "LedDriver.h"

/* Led module を初期化 */
void LedDriver_Init(stc_led_t* this, uint8_t* pLedOutputReg)
{
    this->pLedOutputReg = pLedOutputReg;
}

/* Led をすべて点灯する */
void LedDriver_LedAllOn(stc_led_t* this)
{
    if(this->pLedOutputReg == NULL)
    {
        return;
    }

    *(this->pLedOutputReg) = 0xFFu;
}

/* "ledIdx" により指定されたLED を点灯する */
void LedDriver_LedOn(stc_led_t* this, int ledIdx)
{
    if(this->pLedOutputReg == NULL)
    {
        return;
    }

    if((ledIdx < 1) || (8 < ledIdx))
    {
        return;
    }

    *(this->pLedOutputReg) |= (1u << ledIdx);
}

/* LEDをすべて消灯する */
void LedDriver_LedAllOff(stc_led_t* this)
{
    if(this->pLedOutputReg == NULL)
    {
        return;
    }

    *(this->pLedOutputReg) = 0x0u;
}

/* "ledIdx"により指定されたLEDを消灯する */
void LedDriver_LedOff(stc_led_t* this, int ledIdx)
{
    if(this->pLedOutputReg == NULL)
    {
        return;
    }

    if((ledIdx < 1) || (8 < ledIdx))
    {
        return;
    }

    *(this->pLedOutputReg) &= ~(1u << ledIdx);
}


