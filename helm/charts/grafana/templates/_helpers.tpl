{{- define "grafana.name" -}}
{{- .Chart.Name -}}
{{- end }}

{{- define "grafana.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "grafana.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end }}
