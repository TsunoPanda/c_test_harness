#include "SetAndGet.h"

static int buffer = 0;

void SetValue(int value)
{
    buffer = value;
}

int GetValue(void)
{
    return(buffer);
}


