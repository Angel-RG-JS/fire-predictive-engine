package com.fireproject.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record FireResponse(
        @JsonProperty("years_to_reach_goal") Double yearsToReachGoal,
        @JsonProperty("shortfall") Double shortfall,
        @JsonProperty("reached") Boolean reached,
        @JsonProperty("final_value") Double finalValue,
        @JsonProperty("current_val") Double currentVal,
        @JsonProperty("fire_target") Double fireTarget,
        @JsonProperty("final_estimated_value") Double finalEstimatedValue,
        @JsonProperty("years_simulated") Double yearsSimulated,
        @JsonProperty("monthly_savings") Double monthlySavings,
        @JsonProperty("confidence_score") Double confidenceScore
) {
    public double safeFinalValue() {
        return finalValue != null ? finalValue : 0.0;
    }
}
