#include "LedDriver.h"

#include "CppUTest/TestHarness.h"

/*
    Virtual LED �o�̓��W�X�^
    �^�[�Q�b�g��MCU������LED�o�͂��R���g���[�����郌�W�X�^��z�肵�Ă���B
    �e�X�g����PC��ɂ͑��݂��Ȃ��̂ŁARAM�ϐ��ő�p����B
*/
static uint8_t   virtualLedReg;

static stc_led_t testLedModule;

TEST_GROUP(LedDriver)
{
    void setup()
    {
        /* HW���Z�b�g���G�~�����[�g: LED�o�̓��W�X�^�̏����l��ݒ� */
        virtualLedReg = 0x00u;

        LedDriver_Init(&testLedModule, &virtualLedReg);
    }

    void teardown()
    {
    }
};

TEST(LedDriver, AllLedOn)
{
    LedDriver_LedAllOn(&testLedModule);
    BYTES_EQUAL(virtualLedReg, 0xFFu);
}

TEST(LedDriver, AllLedOff)
{
    LedDriver_LedAllOn(&testLedModule);
    LedDriver_LedAllOff(&testLedModule);
    BYTES_EQUAL(virtualLedReg, 0x0u);
}

TEST(LedDriver, LedOn)
{
    LedDriver_LedAllOff(&testLedModule);
    LedDriver_LedOn(&testLedModule, 4);
    LedDriver_LedOn(&testLedModule, 5);
    BYTES_EQUAL(virtualLedReg, 0x18u);
}

TEST(LedDriver, LedOff)
{
    LedDriver_LedAllOn(&testLedModule);
    LedDriver_LedOff(&testLedModule, 8);
    LedDriver_LedOff(&testLedModule, 1);
    BYTES_EQUAL(virtualLedReg, 0x7Eu);
}


