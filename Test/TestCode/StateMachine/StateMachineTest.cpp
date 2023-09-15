#include "StateMachine.h"

#include "CppUTest/TestHarness.h"
#include "CppUTest/MemoryLeakDetectorMallocMacros.h"

static stc_stmch_t state_machine;

void state1_entry(void* arg)
{
    printf("state1 entry\n");
}

void state1_do(void* arg)
{
    static uint32_t count = 0;
    count += 1;

    if(count > 30)
    {
        StMchn_SetNextState(0, &state_machine);
    }
    if(count > 50)
    {
        StMchn_SetNextState(1, &state_machine);
    }
    printf("state1 do\n");
}

void state1_exit(void* arg)
{
    printf("state1 exit\n");
}

void state2_entry(void* arg)
{
    printf("state2 entry\n");
}

void state2_do(void* arg)
{
    printf("state2 do\n");
}

void state2_exit(void* arg)
{
    printf("state2 exit\n");
}

stc_stmch_func test_state_functions[2] =
{
    {state1_entry, state1_do, state1_exit},
    {state2_entry, state2_do, state2_exit},
};

TEST_GROUP(StateMachin)
{
    void setup()
    {
        uint32_t initial_state = 0;
        uint32_t state_count = 2;
        void* p_argument = NULL;
        StMchn_Init(initial_state, state_count, test_state_functions, p_argument, &state_machine);
    }

    void teardown()
    {
    }
};



TEST(StateMachin, StateChange)
{
    for(uint32_t i = 0; i<100; i+=1)
    {
        printf("******** cycle %d **********\n", i);
        StMchn_Main(&state_machine);
    }
};

