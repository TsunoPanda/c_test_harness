#include "unity_fixture.h"

TEST_GROUP_RUNNER(LedDriver)
{
    RUN_TEST_CASE(LedDriver, AllLedOn);  // tag: TEST_LedDriver_AllLedOn_
    RUN_TEST_CASE(LedDriver, AllLedOff);
    RUN_TEST_CASE(LedDriver, LedOn);
    RUN_TEST_CASE(LedDriver, LedOff);
}

static void RunAllTests(void)
{
    RUN_TEST_GROUP(LedDriver);
}

int main(int argc, const char * argv[])
{
  return UnityMain(argc, argv, RunAllTests);
}

