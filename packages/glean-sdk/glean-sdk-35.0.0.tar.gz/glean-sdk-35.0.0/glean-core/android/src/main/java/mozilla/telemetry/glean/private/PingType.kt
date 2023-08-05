/* This Source Code Form is subject to the terms of the Mozilla Public
* License, v. 2.0. If a copy of the MPL was not distributed with this
* file, You can obtain one at http://mozilla.org/MPL/2.0/. */

package mozilla.telemetry.glean.private

import com.sun.jna.StringArray
import mozilla.telemetry.glean.Glean
import mozilla.telemetry.glean.rust.LibGleanFFI
import mozilla.telemetry.glean.rust.toByte

/**
 * An enum with no values for convenient use as the default set of reason codes.
 */
@Suppress("EmptyClassBlock")
enum class NoReasonCodes(
    /**
     * @suppress
     */
    val value: Int
) {
    // deliberately empty
}

/**
 * The base class of all PingTypes with just enough to track their registration, so
 * we can create a heterogeneous collection of ping types.
 */
open class PingTypeBase(
    internal val name: String
) {
    internal var handle: Long = 0L
}

/**
 * This implements the developer facing API for custom pings.
 *
 * Instances of this class type are automatically generated by the parsers at build time.
 *
 * The Ping API only exposes the [send] method, which schedules a ping for sending.
 *
 * @property reasonCodes The list of acceptable reason codes for this ping.
 */
class PingType<ReasonCodesEnum : Enum<ReasonCodesEnum>> (
    name: String,
    includeClientId: Boolean,
    sendIfEmpty: Boolean,
    val reasonCodes: List<String>
) : PingTypeBase(name) {

    init {
        val ffiReasonList = StringArray(reasonCodes.toTypedArray(), "utf-8")
        val ffiReasonListLen = reasonCodes.size
        this.handle = LibGleanFFI.INSTANCE.glean_new_ping_type(
            name = name,
            include_client_id = includeClientId.toByte(),
            send_if_empty = sendIfEmpty.toByte(),
            reason_codes = ffiReasonList,
            reason_codes_len = ffiReasonListLen
        )
        Glean.registerPingType(this)
    }

    /**
     * Collect and submit the ping for eventual upload.
     *
     * While the collection of metrics into pings happens synchronously, the
     * ping queuing and ping uploading happens asyncronously.
     * There are no guarantees that this will happen immediately.
     *
     * If the ping currently contains no content, it will not be queued.
     *
     * @param reason The reason the ping is being submitted.
     */
    @JvmOverloads
    fun submit(reason: ReasonCodesEnum? = null) {
        val reasonString = reason?.let { this.reasonCodes[it.ordinal] }
        Glean.submitPing(this, reasonString)
    }

    /**
     * Collect and submit the ping for eventual upload.
     *
     * **THIS METHOD IS DEPRECATED.**  Use `submit()` instead.
     *
     * While the collection of metrics into pings happens synchronously, the
     * ping queuing and ping uploading happens asyncronously.
     * There are no guarantees that this will happen immediately.
     *
     * If the ping currently contains no content, it will not be queued.
     */
    @Deprecated("Renamed to submit()")
    fun send() {
        submit()
    }
}
