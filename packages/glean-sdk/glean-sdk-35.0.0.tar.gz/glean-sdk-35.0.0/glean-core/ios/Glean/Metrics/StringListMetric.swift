/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

import Foundation

/// This implements the developer facing API for recording string list metrics.
///
/// Instances of this class type are automatically generated by the parsers at build time,
/// allowing developers to record values that were previously registered in the metrics.yaml file.
///
/// The string list API only exposes the `StringListMetricType.add(_:)` and `StringListMetricType.set(_:)` methods,
/// which takes care of validating the input
/// data and making sure that limits are enforced.
public class StringListMetricType {
    let handle: UInt64
    let disabled: Bool
    let sendInPings: [String]

    /// The public constructor used by automatically generated metrics.
    public init(category: String, name: String, sendInPings: [String], lifetime: Lifetime, disabled: Bool) {
        self.disabled = disabled
        self.sendInPings = sendInPings
        self.handle = withArrayOfCStrings(sendInPings) { pingArray in
            glean_new_string_list_metric(
                category,
                name,
                pingArray,
                Int32(sendInPings.count),
                lifetime.rawValue,
                disabled ? 1 : 0
            )
        }
    }

    /// An internal constructor to be used by the `LabeledMetricType` directly.
    init(withHandle handle: UInt64, disabled: Bool, sendInPings: [String]) {
        self.handle = handle
        self.disabled = disabled
        self.sendInPings = sendInPings
    }

    /// Destroy this metric.
    deinit {
        if self.handle != 0 {
            glean_destroy_string_list_metric(self.handle)
        }
    }

    /// Appends a string value to one or more string list metric stores.  If the string exceeds the
    /// maximum string length or if the list exceeds the maximum length it will be truncated.
    ///
    /// - parameters:
    ///     * value: This is a user defined string value. The maximum length of
    ///              this string is `MAX_STRING_LENGTH`.
    public func add(_ value: String) {
        guard !self.disabled else { return }

        Dispatchers.shared.launchAPI {
            glean_string_list_add(self.handle, value)
        }
    }

    /// Sets a string list to one or more metric stores. If any string exceeds the maximum string
    /// length or if the list exceeds the maximum length it will be truncated.
    ///
    /// - parameters:
    ///    * value: This is a user defined string list.
    public func set(_ value: [String]) {
        guard !self.disabled else { return }

        Dispatchers.shared.launchAPI {
            let len = value.count
            withArrayOfCStrings(value) { value in
                glean_string_list_set(self.handle, value, Int32(len))
            }
        }
    }

    /// Tests whether a value is stored for the metric for testing purposes only. This function will
    /// attempt to await the last task (if any) writing to the the metric's storage engine before
    /// returning a value.
    ///
    /// - parameters:
    ///     * pingName: represents the name of the ping to retrieve the metric for.
    ///                 Defaults to the first value in `sendInPings`.
    /// - returns: true if metric value exists, otherwise false
    public func testHasValue(_ pingName: String? = nil) -> Bool {
        Dispatchers.shared.assertInTestingMode()

        let pingName = pingName ?? self.sendInPings[0]
        return glean_string_list_test_has_value(self.handle, pingName).toBool()
    }

    /// Returns the stored value for testing purposes only. This function will attempt to await the
    /// last task (if any) writing to the the metric's storage engine before returning a value.
    ///
    /// Throws a "Missing value" exception if no value is stored.
    ///
    /// - parameters:
    ///     * pingName: represents the name of the ping to retrieve the metric for.
    ///                 Defaults to the first value in `sendInPings`.
    ///
    /// - returns:  value of the stored metric
    public func testGetValue(_ pingName: String? = nil) throws -> [String] {
        Dispatchers.shared.assertInTestingMode()

        let pingName = pingName ?? self.sendInPings[0]

        if !testHasValue(pingName) {
            throw "Missing value"
        }

        let cstr = glean_string_list_test_get_value_as_json_string(self.handle, pingName)!
        let json = String(freeingGleanString: cstr)
        let data = json.data(using: .utf8)!
        if let content = try JSONSerialization.jsonObject(with: data, options: []) as? [String] {
            return content
        } else {
            throw "Missing value"
        }
    }

    /// Returns the number of errors recorded for the given metric.
    ///
    /// - parameters:
    ///     * errorType: The type of error recorded.
    ///     * pingName: represents the name of the ping to retrieve the metric for.
    ///                 Defaults to the first value in `sendInPings`.
    ///
    /// - returns: The number of errors recorded for the metric for the given error type.
    public func testGetNumRecordedErrors(_ errorType: ErrorType, pingName: String? = nil) -> Int32 {
        Dispatchers.shared.assertInTestingMode()

        let pingName = pingName ?? self.sendInPings[0]

        return glean_string_list_test_get_num_recorded_errors(
            self.handle,
            errorType.rawValue,
            pingName
        )
    }
}
