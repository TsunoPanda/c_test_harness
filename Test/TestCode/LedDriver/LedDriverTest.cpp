#include "LedDriver.h"

#include "CppUTest/TestHarness.h"

/*
    Virtual LED 出力レジスタ
    ターゲットのMCUが持つLED出力をコントロールするレジスタを想定している。
    テスト環境のPC上には存在しないので、RAM変数で代用する。
*/
static uint8_t   virtualLedReg;

static stc_led_t testLedModule;

TEST_GROUP(LedDriver)
{
    void setup()
    {
        /* HWリセットをエミュレート: LED出力レジスタの初期値を設定 */
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


