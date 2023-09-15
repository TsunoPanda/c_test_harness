#ifndef __STATEMACHINE_H__
#define __STATEMACHINE_H__

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define STMCHN_INVALID_STATE (0xFFFFFFFFul) /* Invalid state value */

typedef void (*StMchFunc)(void* pParam);

/* Structure which contains pointers to functions which are called according to its state */
typedef struct
{
    StMchFunc entryFunc;  /* Pointer to a function which called one time when it enters to the state */
    StMchFunc cyclicFunc; /* Pointer to a function which called periodically in the state */
    StMchFunc exitFunc;   /* Pointer to a function which called one time when it exits from the state */
} stc_stmch_func;

/* Structure of state machine member */
typedef struct
{
    uint32_t        previousState; /* Having previous state only a moment current state changed */
    uint32_t        currentState;  /* Keeps current state */
    uint32_t        nextState;     /* Next state which user set using "StMchn_SetNextState" */
    uint32_t        stateMaxCount; /* State maximum count */
    stc_stmch_func* stateFuncs;    /* Pointer to top of an array of "stc_stmch_func" which user defined */
    void*           pParam;        /* Pointer to parameter to be input to each function */
} stc_stmch_t;


bool     StMchn_Init(uint32_t initialState, uint32_t stateCount, stc_stmch_func* stateFuncs, void* pParam, stc_stmch_t* m);
bool     StMchn_Main(stc_stmch_t* m);
bool     StMchn_SetNextState(uint32_t stateIdx, stc_stmch_t* m);
uint32_t StMchn_GetCurrentState(stc_stmch_t* m);
uint32_t StMchn_GetPreviousState(stc_stmch_t* m);
uint32_t StMchn_GetNextState(stc_stmch_t* m);

#endif // __STATEMACHINE_H__
