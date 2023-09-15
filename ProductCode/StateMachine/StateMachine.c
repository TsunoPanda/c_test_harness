#include "StateMachine.h"


/*******************************************************************************
* Function Name: StMchn_Init
****************************************************************************//**
*
* This function initialize state machine member variables. Please call this
* function before you call any other functions in this file.
*
* \param initialState
*        Initial state of the state machine
*
* \param stateCount
*        Number of status which user defined
*
* \param stateFuncs
*        Pointer to the top of an array of "stc_stmch_func" which user defined.
*
* \param m
*        Pointer to a member variables of the state machine
*
* \return true : succeeded
*         false: failed
*
*******************************************************************************/
bool StMchn_Init(uint32_t initialState, uint32_t stateCount, stc_stmch_func* stateFuncs, void* pParam, stc_stmch_t* m)
{
    if(m == NULL)
    {
        return false;
    }

    m->previousState = STMCHN_INVALID_STATE;
    m->currentState  = initialState;
    m->nextState     = initialState;
    m->stateMaxCount = stateCount;
    m->stateFuncs    = stateFuncs;
    m->pParam        = pParam;
    return true;
}

/*******************************************************************************
* Function Name: StMchn_Main
****************************************************************************//**
*
* This function controls the state machine and calls entry/exit/cyclic functions 
* according to current state and state change. Please call this function in the 
* periodic loop.
*
* \param m
*        Pointer to a member variables of the state machine
*
* \return true : succeeded
*         false: failed
*
* \note
*
*******************************************************************************/
bool StMchn_Main(stc_stmch_t* m)
{
    if(m == NULL)
    {
        return false;
    }

    if(m->stateFuncs == NULL)
    {
        return false;
    }

    // 1. check if current state is not bigger than max state number.
    if(m->currentState > m->stateMaxCount)
    {
        m->currentState = m->stateMaxCount;
    }

    // 2. Execute the beginning function. if the state has been changed.
    if(m->currentState != m->previousState)
    {
        if(m->stateFuncs[m->currentState].entryFunc != NULL)
        {
            m->stateFuncs[m->currentState].entryFunc(m->pParam);
        }
        m->previousState = m->currentState;
    }

    // 3. Execute the main (cyclic) function, if next state have not been changed
    if(m->nextState == m->currentState)
    {
        if(m->stateFuncs[m->currentState].cyclicFunc != NULL)
        {
            m->stateFuncs[m->currentState].cyclicFunc(m->pParam);
        }
    }

    // 4. Execute the ending function, if the state has been changed.
    // Note "nextState" is subject to be changed by user.
    uint32_t nextStateSaved = m->nextState;
    if(nextStateSaved != m->currentState)
    {
        if(m->stateFuncs[m->currentState].exitFunc != NULL)
        {
            m->stateFuncs[m->currentState].exitFunc(m->pParam);
        }
        m->currentState = nextStateSaved;
    }

    return true;
}

/*******************************************************************************
* Function Name: StMchn_SetNextState
****************************************************************************//**
*
* This function changes state of the state machine.
*
* \param stateIdx
*        State which current state will change into.
*
* \param m
*        Pointer to a member variables of the state machine
*
* \return true : succeeded
*         false: failed
*
* \note
*
*******************************************************************************/
bool StMchn_SetNextState(uint32_t stateIdx, stc_stmch_t* m)
{
    if(m == NULL)
    {
        return false;
    }

    if(stateIdx >= m->stateMaxCount)
    {
        return false;
    }

    m->nextState = stateIdx;
    return true;
}

/*******************************************************************************
* Function Name: StMchn_GetCurrentState
****************************************************************************//**
*
* This function returns current state of the state machine.
*
* \param m
*        Pointer to a member variables of the state machine
*
* \return current state
*
* \note
*
*******************************************************************************/
uint32_t StMchn_GetCurrentState(stc_stmch_t* m)
{
    if(m == NULL)
    {
        return STMCHN_INVALID_STATE;
    }

    return(m->currentState);
}

/*******************************************************************************
* Function Name: StMchn_GetPreviousState
****************************************************************************//**
*
* This function returns previous state but only in the entrance routine.
*
* \param m
*        Pointer to a member variables of the state machine
*
* \return previous state
*
* \note
* Valid only in entrance routine. if not in entrance routine, previous state
* should be same as current state
*
*******************************************************************************/
uint32_t StMchn_GetPreviousState(stc_stmch_t* m)
{
    if(m == NULL)
    {
        return STMCHN_INVALID_STATE;
    }

    return(m->previousState);
}

/*******************************************************************************
* Function Name: StMchn_GetNextState
****************************************************************************//**
*
* This function returns next state but only in the exit routine.
*
* \param m
*        Pointer to a member variables of the state machine
*
* \return next state
*
* \note
* Valid only in exit routine. if not in exit routine, next state
* should be same as current state
*
*******************************************************************************/
uint32_t StMchn_GetNextState(stc_stmch_t* m)
{
    if(m == NULL)
    {
        return STMCHN_INVALID_STATE;
    }

    return(m->nextState);
}

