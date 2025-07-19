{{- define "prometheus.name" -}}
{{- .Chart.Name -}}
{{- end }}

{{- define "prometheus.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "prometheus.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end }}
