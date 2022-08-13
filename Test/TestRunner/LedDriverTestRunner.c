#include "unity_fixture.h"

TEST_GROUP_RUNNER(LedDriver)
{
    RUN_TEST_CASE(LedDriver, AllLedOn);  // tag: TEST_LedDriver_AllLedOn_
    RUN_TEST_CASE(LedDriver, AllLedOff);
    RUN_TEST_CASE(LedDriver, LedOn);
    RUN_TEST_CASE(LedDriver, LedOff);
}

