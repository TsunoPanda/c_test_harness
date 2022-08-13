/* Vector Cast �f���p�̃R�[�h: �f�o�b�O�O */

#include "LedDriver.h"

/* Led module �������� */
void LedDriver_Init(stc_led_t* this, uint8_t* pLedOutputReg)
{
    this->pLedOutputReg = pLedOutputReg;
}

/* Led �����ׂē_������ */
void LedDriver_LedAllOn(stc_led_t* this)
{
    if(this->pLedOutputReg == NULL)
    {
        return;
    }

    *(this->pLedOutputReg) = 0xFFu;
}

/* "ledIdx" �ɂ��w�肳�ꂽLED ��_������ */
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

/* LED�����ׂď������� */
void LedDriver_LedAllOff(stc_led_t* this)
{
    if(this->pLedOutputReg == NULL)
    {
        return;
    }

    *(this->pLedOutputReg) = 0x0u;
}

/* "ledIdx"�ɂ��w�肳�ꂽLED���������� */
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


