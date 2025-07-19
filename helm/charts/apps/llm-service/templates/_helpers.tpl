{{/*
Expand the simple name of the chart.
*/}}
{{- define "llmservice.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Create a fully qualified app name
*/}}
{{- define "llmservice.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "llmservice.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end }}

{{/*
Labels
*/}}
{{- define "llmservice.labels" -}}
app.kubernetes.io/name: {{ include "llmservice.name" . }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "llmservice.selectorLabels" -}}
app.kubernetes.io/name: {{ include "llmservice.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
