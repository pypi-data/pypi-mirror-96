﻿// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using Mozilla.Glean.FFI;
using Mozilla.Glean.Utils;
using System;

namespace Mozilla.Glean.Private
{
    /// <summary>
    /// An opaque type representing a Glean timer.
    /// </summary>
    public class GleanTimerId
    {
        private readonly ulong timerId;

        // Don't allow direct instantiations.
        private GleanTimerId() { }

        private GleanTimerId(ulong id)
        {
            timerId = id;
        }

        public static implicit operator ulong(GleanTimerId id) => id.timerId;
        public static explicit operator GleanTimerId(ulong b) => new GleanTimerId(b);
    }

    /// <summary>
    /// This implements the developer facing API for recording timing distribution metrics.
    ///
    /// Instances of this class type are automatically generated by the parsers at build time,
    /// allowing developers to record values that were previously registered in the metrics.yaml file.
    /// </summary>
    public sealed class TimingDistributionMetricType
    {
        private bool disabled;
        private string[] sendInPings;
        private UInt64 handle;

        /// <summary>
        /// The public constructor used by automatically generated metrics.
        /// </summary>
        public TimingDistributionMetricType(
            bool disabled,
            string category,
            Lifetime lifetime,
            string name,
            string[] sendInPings,
            TimeUnit timeUnit = TimeUnit.Minute
            ) : this(0, disabled, sendInPings)
        {
            handle = LibGleanFFI.glean_new_timing_distribution_metric(
                        category: category,
                        name: name,
                        send_in_pings: sendInPings,
                        send_in_pings_len: sendInPings.Length,
                        lifetime: (int)lifetime,
                        disabled: disabled,
                        time_unit: (int)timeUnit
                        );
        }

        internal TimingDistributionMetricType(
            UInt64 handle,
            bool disabled,
            string[] sendInPings
            )
        {
            this.disabled = disabled;
            this.sendInPings = sendInPings;
            this.handle = handle;
        }

        /// <summary>
        /// Start tracking time for the provided metric. This records an error if
        /// it’s already tracking time (i.e. start was already called with no
        /// corresponding `StopAndAccumulate`): in that case the original start time will
        /// be preserved.
        /// </summary>
        /// <returns>
        /// The `GleanTimerId` object to associate with this timing or `null`
        /// if the collection was disabled.
        /// </returns>
        public GleanTimerId Start()
        {
            if (disabled)
            {
                return null;
            }

            // Even though the Rust code for `Start` runs synchronously, the Rust
            // code for `StopAndAccumulate` runs asynchronously, and we need to use the same
            // clock for start and stop. Therefore we take the time on the C# side, both
            // here and in `StopAndAccumulate`.
            ulong startTime = HighPrecisionTimestamp.GetTimestamp(TimeUnit.Nanosecond);

            // No dispatcher, we need the return value
            return (GleanTimerId)LibGleanFFI.glean_timing_distribution_set_start(handle, startTime);
        }

        /// <summary>
        /// Stop tracking time for the provided metric and associated timer id. Add a
        /// count to the corresponding bucket in the timing distribution.
        /// This will record an error if no `Start` was called.
        /// </summary>
        /// <param name="timerId">
        /// The `GleanTimerId` associated with this timing.  This allows for concurrent
        /// timing of events associated with different ids to the same timing distribution.
        /// </param>
        public void StopAndAccumulate(GleanTimerId timerId)
        {
            // `Start` might return null.
            // Accepting that means users of this API don't need to do a null check.
            if (disabled || timerId == null)
            {
                return;
            }

            // The Rust code runs async and might be delayed. We need the time as precise as possible.
            // We also need the same clock for start and stop (`Start` takes the time on the C# side).
            ulong stopTime = HighPrecisionTimestamp.GetTimestamp(TimeUnit.Nanosecond);

            Dispatchers.LaunchAPI(() =>
            {
                LibGleanFFI.glean_timing_distribution_set_stop_and_accumulate(
                    handle,
                    timerId,
                    stopTime
                );
            });
        }


        ///<summary>
        /// Convenience method to simplify measuring a function or block of code
        ///
        /// If the measured function throws, the measurement is canceled and the exception rethrown.
        /// </summary>
        /// <exception>
        /// If the measured function throws, the measurement is
        /// canceled and the exception rethrown.
        /// </exception>
        public T Measure<T>(Func<T> funcToMeasure)
        {
            GleanTimerId timerId = Start();

            T returnValue;

            try
            {
                returnValue = funcToMeasure();
            }
            catch (Exception e)
            {
                Cancel(timerId);
                throw e;
            }

            StopAndAccumulate(timerId);

            return returnValue;
        }

        /// <summary>
        /// Abort a previous `Start` call. No error is recorded if no `Start` was called.
        /// </summary>
        /// <param name="timerId">
        /// The `GleanTimerId` associated with this timing. This allows for concurrent timing
        /// of events associated with different ids to the same timing distribution metric.
        /// </param>
        public void Cancel(GleanTimerId timerId)
        {
            if (disabled || timerId == null)
            {
                return;
            }

            Dispatchers.LaunchAPI(() =>
            {
                LibGleanFFI.glean_timing_distribution_cancel(handle, timerId);
            });
        }

        /// <summary>
        /// Tests whether a value is stored for the metric for testing purposes only. This function will
        /// attempt to await the last task (if any) writing to the the metric's storage engine before
        /// returning a value.
        /// </summary>
        /// <param name="pingName">represents the name of the ping to retrieve the metric for Defaults
        /// to the first value in `sendInPings`</param>
        /// <returns>true if metric value exists, otherwise false</returns>
        public bool TestHasValue(string pingName = null)
        {
            Dispatchers.AssertInTestingMode();

            string ping = pingName ?? sendInPings[0];
            return LibGleanFFI.glean_timing_distribution_test_has_value(handle, ping) != 0;
        }

        /// <summary>
        /// Returns the stored value for testing purposes only. This function will attempt to await the
        /// last task (if any) writing to the the metric's storage engine before returning a value.
        /// </summary>
        /// <param name="pingName">represents the name of the ping to retrieve the metric for.
        /// Defaults to the first value in `sendInPings`</param>
        /// <returns>value of the stored metric</returns>
        /// <exception cref="System.NullReferenceException">Thrown when the metric contains no value</exception>
        public DistributionData TestGetValue(string pingName = null)
        {
            Dispatchers.AssertInTestingMode();

            if (!TestHasValue(pingName))
            {
                throw new NullReferenceException();
            }

            string ping = pingName ?? sendInPings[0];
            return DistributionData.FromJsonString(
                LibGleanFFI.glean_timing_distribution_test_get_value_as_json_string(handle, ping).AsString());
        }

        /// <summary>
        /// Returns the number of errors recorded for the given metric.
        /// </summary>
        /// <param name="errorType">the type of the error recorded.</param>
        /// <param name="pingName">represents the name of the ping to retrieve the metric for.
        /// Defaults to the first value in `sendInPings`.</param>
        /// <returns>the number of errors recorded for the metric.</returns>
        public Int32 TestGetNumRecordedErrors(Testing.ErrorType errorType, string pingName = null)
        {
            Dispatchers.AssertInTestingMode();

            string ping = pingName ?? sendInPings[0];
            return LibGleanFFI.glean_timing_distribution_test_get_num_recorded_errors(
                handle, (int)errorType, ping
            );
        }
    }
}
