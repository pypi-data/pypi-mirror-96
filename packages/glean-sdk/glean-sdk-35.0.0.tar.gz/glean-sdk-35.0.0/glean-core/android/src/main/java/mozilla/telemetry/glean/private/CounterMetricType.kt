/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

package mozilla.telemetry.glean.private

import androidx.annotation.VisibleForTesting
import com.sun.jna.StringArray
import mozilla.telemetry.glean.Dispatchers
import mozilla.telemetry.glean.rust.LibGleanFFI
import mozilla.telemetry.glean.rust.toBoolean
import mozilla.telemetry.glean.rust.toByte
import mozilla.telemetry.glean.testing.ErrorType

/**
 * This implements the developer facing API for recording counter metrics.
 *
 * Instances of this class type are automatically generated by the parsers at build time,
 * allowing developers to record values that were previously registered in the metrics.yaml file.
 *
 * The counter API only exposes the [add] method, which takes care of validating the input
 * data and making sure that limits are enforced.
 *
 * The internal constructor is only used by [LabeledMetricType] directly.
 */
class CounterMetricType internal constructor(
    private var handle: Long,
    private val disabled: Boolean,
    private val sendInPings: List<String>
) {
    /**
     * The public constructor used by automatically generated metrics.
     */
    constructor(
        disabled: Boolean,
        category: String,
        lifetime: Lifetime,
        name: String,
        sendInPings: List<String>
    ) : this(handle = 0, disabled = disabled, sendInPings = sendInPings) {
        val ffiPingsList = StringArray(sendInPings.toTypedArray(), "utf-8")
        this.handle = LibGleanFFI.INSTANCE.glean_new_counter_metric(
                category = category,
                name = name,
                send_in_pings = ffiPingsList,
                send_in_pings_len = sendInPings.size,
                lifetime = lifetime.ordinal,
                disabled = disabled.toByte())
    }

    /**
     * Add to counter value.
     *
     * @param amount This is the amount to increment the counter by, defaulting to 1 if called
     * without parameters.
     */
    @JvmOverloads
    fun add(amount: Int = 1) {
        if (disabled) {
            return
        }

        @Suppress("EXPERIMENTAL_API_USAGE")
        Dispatchers.API.launch {
            LibGleanFFI.INSTANCE.glean_counter_add(
                this@CounterMetricType.handle,
                amount)
        }
    }

    /**
     * Add to counter value synchronously.
     *
     * This is only to be used for the glean-ac to glean-core data migration.
     *
     * @param amount This is the amount to increment the counter by.
     */
    internal fun addSync(amount: Int) {
        if (disabled) {
            return
        }

        LibGleanFFI.INSTANCE.glean_counter_add(
            this@CounterMetricType.handle,
            amount
        )
    }

    /**
     * Tests whether a value is stored for the metric for testing purposes only. This function will
     * attempt to await the last task (if any) writing to the the metric's storage engine before
     * returning a value.
     *
     * @param pingName represents the name of the ping to retrieve the metric for.
     *                 Defaults to the first value in `sendInPings`.
     * @return true if metric value exists, otherwise false
     */
    @VisibleForTesting(otherwise = VisibleForTesting.NONE)
    @JvmOverloads
    fun testHasValue(pingName: String = sendInPings.first()): Boolean {
        @Suppress("EXPERIMENTAL_API_USAGE")
        Dispatchers.API.assertInTestingMode()

        val res = LibGleanFFI.INSTANCE.glean_counter_test_has_value(this.handle, pingName)
        return res.toBoolean()
    }

    /**
     * Returns the stored value for testing purposes only. This function will attempt to await the
     * last task (if any) writing to the the metric's storage engine before returning a value.
     *
     * @param pingName represents the name of the ping to retrieve the metric for.
     *                 Defaults to the first value in `sendInPings`.
     * @return value of the stored metric
     * @throws [NullPointerException] if no value is stored
     */
    @VisibleForTesting(otherwise = VisibleForTesting.NONE)
    @JvmOverloads
    fun testGetValue(pingName: String = sendInPings.first()): Int {
        @Suppress("EXPERIMENTAL_API_USAGE")
        Dispatchers.API.assertInTestingMode()

        if (!testHasValue(pingName)) {
            throw NullPointerException("Metric has no value")
        }
        return LibGleanFFI.INSTANCE.glean_counter_test_get_value(this.handle, pingName)
    }

    /**
     * Returns the number of errors recorded for the given metric.
     *
     * @param errorType The type of the error recorded.
     * @param pingName represents the name of the ping to retrieve the metric for.
     *                 Defaults to the first value in `sendInPings`.
     * @return the number of errors recorded for the metric.
     */
    @VisibleForTesting(otherwise = VisibleForTesting.NONE)
    @JvmOverloads
    fun testGetNumRecordedErrors(errorType: ErrorType, pingName: String = sendInPings.first()): Int {
        @Suppress("EXPERIMENTAL_API_USAGE")
        Dispatchers.API.assertInTestingMode()

        return LibGleanFFI.INSTANCE.glean_counter_test_get_num_recorded_errors(
            this.handle, errorType.ordinal, pingName
        )
    }
}
