/*
 *
 * std.c
 *
 * Code generation for function 'std'
 *
 */

/* Include files */
#include "std.h"
#include "fetch_thresholds.h"
#include "fetch_thresholds_emxutil.h"
#include "rt_nonfinite.h"
#include <math.h>

/* Function Definitions */

/*
 *
 */
double b_std(const emxArray_real_T *x)
{
  double y;
  int n;
  double xbar;
  int k;
  emxArray_real_T *absdiff;
  int kend;
  double t;
  n = x->size[0];
  if (x->size[0] == 0) {
    y = rtNaN;
  } else if (x->size[0] == 1) {
    if ((!rtIsInf(x->data[0])) && (!rtIsNaN(x->data[0]))) {
      y = 0.0;
    } else {
      y = rtNaN;
    }
  } else {
    xbar = x->data[0];
    for (k = 2; k <= n; k++) {
      xbar += x->data[k - 1];
    }

    emxInit_real_T(&absdiff, 1);
    xbar /= (double)x->size[0];
    kend = absdiff->size[0];
    absdiff->size[0] = x->size[0];
    emxEnsureCapacity_real_T(absdiff, kend);
    for (k = 0; k < n; k++) {
      absdiff->data[k] = fabs(x->data[k] - xbar);
    }

    y = 0.0;
    xbar = 3.3121686421112381E-170;
    kend = x->size[0];
    for (k = 0; k < kend; k++) {
      if (absdiff->data[k] > xbar) {
        t = xbar / absdiff->data[k];
        y = y * t * t + 1.0;
        xbar = absdiff->data[k];
      } else {
        t = absdiff->data[k] / xbar;
        y += t * t;
      }
    }

    emxFree_real_T(&absdiff);
    y = xbar * sqrt(y);
    y /= sqrt((double)x->size[0] - 1.0);
  }

  return y;
}

/* End of code generation (std.c) */
