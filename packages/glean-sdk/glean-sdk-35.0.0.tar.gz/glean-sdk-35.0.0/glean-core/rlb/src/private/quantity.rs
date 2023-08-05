// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.

use inherent::inherent;
use std::sync::Arc;

use glean_core::metrics::MetricType;
use glean_core::ErrorType;

// We need to wrap the glean-core type, otherwise if we try to implement
// the trait for the metric in `glean_core::metrics` we hit error[E0117]:
// only traits defined in the current crate can be implemented for arbitrary
// types.

/// Developer-facing API for recording quantity metrics.
///
/// Instances of this class type are automatically generated by the parsers
/// at build time, allowing developers to record values that were previously
/// registered in the metrics.yaml file.
#[derive(Clone)]
pub struct QuantityMetric(pub(crate) Arc<glean_core::metrics::QuantityMetric>);

impl QuantityMetric {
    /// The public constructor used by automatically generated metrics.
    pub fn new(meta: glean_core::CommonMetricData) -> Self {
        Self(Arc::new(glean_core::metrics::QuantityMetric::new(meta)))
    }
}

#[inherent(pub)]
impl glean_core::traits::Quantity for QuantityMetric {
    fn set(&self, value: i64) {
        let metric = Arc::clone(&self.0);
        crate::launch_with_glean(move |glean| metric.set(glean, value));
    }

    fn test_get_value<'a, S: Into<Option<&'a str>>>(&self, ping_name: S) -> Option<i64> {
        crate::block_on_dispatcher();

        let queried_ping_name = ping_name
            .into()
            .unwrap_or_else(|| &self.0.meta().send_in_pings[0]);

        crate::with_glean(|glean| self.0.test_get_value(glean, queried_ping_name))
    }

    #[allow(dead_code)] // Remove after mozilla/glean#1328
    fn test_get_num_recorded_errors<'a, S: Into<Option<&'a str>>>(
        &self,
        error: ErrorType,
        ping_name: S,
    ) -> i32 {
        crate::block_on_dispatcher();

        crate::with_glean_mut(|glean| {
            glean_core::test_get_num_recorded_errors(&glean, self.0.meta(), error, ping_name.into())
                .unwrap_or(0)
        })
    }
}
