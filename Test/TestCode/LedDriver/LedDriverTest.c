#include "unity.h"
#include "unity_fixture.h"
#include "LedDriver.h"

TEST_GROUP(LedDriver);

/*
    Virtual LED 出力レジスタ
    ターゲットのMCUが持つLED出力をコントロールするレジスタを想定している。
    テスト環境のPC上には存在しないので、RAM変数で代用する。
*/
static uint8_t   virtualLedReg;

static stc_led_t testLedModule;

TEST_SETUP(LedDriver)
{
    /* HWリセットをエミュレート: LED出力レジスタの初期値を設定 */
    virtualLedReg = 0x00u;

    LedDriver_Init(&testLedModule, &virtualLedReg);
}

TEST_TEAR_DOWN(LedDriver)
{
}

TEST(LedDriver, AllLedOn)
{
    LedDriver_LedAllOn(&testLedModule);
    TEST_ASSERT_EQUAL_UINT8(virtualLedReg, 0xFFu);
}

TEST(LedDriver, AllLedOff)
{
    LedDriver_LedAllOn(&testLedModule);
    LedDriver_LedAllOff(&testLedModule);
    TEST_ASSERT_EQUAL_UINT8(virtualLedReg, 0x0u);
}

TEST(LedDriver, LedOn)
{
    LedDriver_LedAllOff(&testLedModule);
    LedDriver_LedOn(&testLedModule, 4);
    LedDriver_LedOn(&testLedModule, 5);
    TEST_ASSERT_EQUAL_UINT8(virtualLedReg, 0x18u);
}

TEST(LedDriver, LedOff)
{
    LedDriver_LedAllOn(&testLedModule);
    LedDriver_LedOff(&testLedModule, 8);
    LedDriver_LedOff(&testLedModule, 1);
    TEST_ASSERT_EQUAL_UINT8(virtualLedReg, 0x7Eu);
}

