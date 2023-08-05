// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

use crate::private::{StringMetric, TimespanMetric};
use crate::{CommonMetricData, Lifetime, TimeUnit};

use once_cell::sync::Lazy;

/// Metrics included in every ping as `client_info`.
#[derive(Debug)]
pub struct ClientInfoMetrics {
    /// The build identifier generated by the CI system (e.g. "1234/A").
    pub app_build: String,
    /// The user visible version string (e.g. "1.0.3").
    pub app_display_version: String,
}

impl ClientInfoMetrics {
    /// Creates the client info with dummy values for all.
    pub fn unknown() -> Self {
        ClientInfoMetrics {
            app_build: "unknown".to_string(),
            app_display_version: "unknown".to_string(),
        }
    }
}

#[allow(non_upper_case_globals)]
pub mod internal_metrics {
    use super::*;

    pub static app_build: Lazy<StringMetric> = Lazy::new(|| {
        StringMetric::new(CommonMetricData {
            name: "app_build".into(),
            category: "".into(),
            send_in_pings: vec!["glean_client_info".into()],
            lifetime: Lifetime::Application,
            disabled: false,
            ..Default::default()
        })
    });

    pub static app_display_version: Lazy<StringMetric> = Lazy::new(|| {
        StringMetric::new(CommonMetricData {
            name: "app_display_version".into(),
            category: "".into(),
            send_in_pings: vec!["glean_client_info".into()],
            lifetime: Lifetime::Application,
            disabled: false,
            ..Default::default()
        })
    });

    pub static app_channel: Lazy<StringMetric> = Lazy::new(|| {
        StringMetric::new(CommonMetricData {
            name: "app_channel".into(),
            category: "".into(),
            send_in_pings: vec!["glean_client_info".into()],
            lifetime: Lifetime::Application,
            disabled: false,
            ..Default::default()
        })
    });

    pub static os_version: Lazy<StringMetric> = Lazy::new(|| {
        StringMetric::new(CommonMetricData {
            name: "os_version".into(),
            category: "".into(),
            send_in_pings: vec!["glean_client_info".into()],
            lifetime: Lifetime::Application,
            disabled: false,
            ..Default::default()
        })
    });

    pub static architecture: Lazy<StringMetric> = Lazy::new(|| {
        StringMetric::new(CommonMetricData {
            name: "architecture".into(),
            category: "".into(),
            send_in_pings: vec!["glean_client_info".into()],
            lifetime: Lifetime::Application,
            disabled: false,
            ..Default::default()
        })
    });

    pub static device_manufacturer: Lazy<StringMetric> = Lazy::new(|| {
        StringMetric::new(CommonMetricData {
            name: "device_manufacturer".into(),
            category: "".into(),
            send_in_pings: vec!["glean_client_info".into()],
            lifetime: Lifetime::Application,
            disabled: false,
            ..Default::default()
        })
    });

    pub static device_model: Lazy<StringMetric> = Lazy::new(|| {
        StringMetric::new(CommonMetricData {
            name: "device_model".into(),
            category: "".into(),
            send_in_pings: vec!["glean_client_info".into()],
            lifetime: Lifetime::Application,
            disabled: false,
            ..Default::default()
        })
    });

    pub static baseline_duration: Lazy<TimespanMetric> = Lazy::new(|| {
        TimespanMetric::new(
            CommonMetricData {
                name: "duration".into(),
                category: "glean.baseline".into(),
                send_in_pings: vec!["baseline".into()],
                lifetime: Lifetime::Ping,
                disabled: false,
                ..Default::default()
            },
            TimeUnit::Second,
        )
    });
}
