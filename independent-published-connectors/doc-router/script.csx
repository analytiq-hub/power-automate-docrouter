// Injects the organization ID from the connection into every request path (/v0/orgs/{organization_id}/...).
// Connection parameter docrouter_organization_id is available as a request header (same pattern as
// microsoft/PowerPlatformConnectors certified connectors — e.g. QPP NextGen, Zoho Invoice Basic).
//
// Upload/Update declare metadata as a string in OpenAPI (Power Automate-friendly); this script parses
// JSON object strings and replaces them with real JSON objects before the request reaches DocRouter.
using System.Text;
using Newtonsoft.Json;

public class Script : ScriptBase
{
    // Policy setheader + runtime may use these names; try in order (see apiProperties policyTemplateInstances).
    private static readonly string[] OrgConnectionHeaderNames = new[]
    {
        "docrouter_organization_id",
        "organization_id"
    };

    private const string OrgPathMarker = "/v0/orgs/";

    public override async Task<HttpResponseMessage> ExecuteAsync()
    {
        if (!TryGetOrganizationIdFromConnection(out var organizationId))
        {
            this.Context.Logger.LogError(
                "Missing organization id header (tried: {0}).",
                string.Join(", ", OrgConnectionHeaderNames));
            return BadRequest(
                "DocRouter organization ID is missing. Set Organization ID when creating the connection.");
        }

        organizationId = organizationId.Trim();
        if (string.IsNullOrEmpty(organizationId))
        {
            return BadRequest(
                "DocRouter organization ID is empty. Set Organization ID when creating the connection.");
        }

        if (!TryRewriteOrgSegment(organizationId, out var errorMessage))
        {
            this.Context.Logger.LogError("Path rewrite failed: {0}", errorMessage ?? "(unknown)");
            return BadRequest(
                "Could not apply organization to the request URL. " + (errorMessage ?? "Unknown error."));
        }

        var metadataError = await TryCoerceMetadataJsonStringsAsync().ConfigureAwait(false);
        if (metadataError != null)
        {
            return metadataError;
        }

        RemoveConnectionOnlyHeaders();

        return await this.Context.SendAsync(this.Context.Request, this.CancellationToken)
            .ConfigureAwait(false);
    }

    private bool TryGetOrganizationIdFromConnection(out string organizationId)
    {
        organizationId = null;
        foreach (var headerName in OrgConnectionHeaderNames)
        {
            if (!this.Context.Request.Headers.TryGetValues(headerName, out var values))
            {
                continue;
            }

            foreach (var v in values)
            {
                if (!string.IsNullOrWhiteSpace(v))
                {
                    organizationId = v;
                    return true;
                }
            }
        }

        return false;
    }

    /// <summary>
    /// Replaces the first path segment after /v0/orgs/ with the connection org id
    /// (fixes placeholder, empty, or undefined segments from the runtime).
    /// </summary>
    private bool TryRewriteOrgSegment(string organizationId, out string errorMessage)
    {
        errorMessage = null;
        var uri = this.Context.Request.RequestUri;
        if (uri == null)
        {
            errorMessage = "RequestUri is null.";
            return false;
        }

        var path = uri.AbsolutePath ?? string.Empty;
        var idx = path.IndexOf(OrgPathMarker, StringComparison.Ordinal);
        if (idx < 0)
        {
            errorMessage = "Path does not contain " + OrgPathMarker;
            return false;
        }

        var segmentStart = idx + OrgPathMarker.Length;
        var encodedOrg = Uri.EscapeDataString(organizationId);
        var nextSlash = path.IndexOf('/', segmentStart);
        string newPath;
        if (nextSlash < 0)
        {
            newPath = path.Substring(0, segmentStart) + encodedOrg;
        }
        else
        {
            newPath = path.Substring(0, segmentStart) + encodedOrg + path.Substring(nextSlash);
        }
        var builder = new UriBuilder(uri) { Path = newPath };
        this.Context.Request.RequestUri = builder.Uri;
        this.Context.Logger.LogInformation(
            "Rewrote organization segment in request path for operation {0}.",
            this.Context.OperationId);
        return true;
    }

    private void RemoveConnectionOnlyHeaders()
    {
        foreach (var headerName in OrgConnectionHeaderNames)
        {
            if (this.Context.Request.Headers.Contains(headerName))
            {
                this.Context.Request.Headers.Remove(headerName);
            }
        }
    }

    /// <summary>
    /// OpenAPI exposes metadata as string for Power Automate; DocRouter expects a JSON object.
    /// Coerces string values to objects; leaves existing JSON objects unchanged.
    /// </summary>
    private async Task<HttpResponseMessage> TryCoerceMetadataJsonStringsAsync()
    {
        var req = this.Context.Request;
        if (req?.Content == null)
        {
            return null;
        }

        var mediaType = req.Content.Headers.ContentType?.MediaType;
        if (string.IsNullOrEmpty(mediaType) ||
            mediaType.IndexOf("json", StringComparison.OrdinalIgnoreCase) < 0)
        {
            return null;
        }

        string json;
        try
        {
            json = await req.Content.ReadAsStringAsync().ConfigureAwait(false);
        }
        catch
        {
            return null;
        }

        if (string.IsNullOrWhiteSpace(json))
        {
            return null;
        }

        JToken root;
        try
        {
            root = JToken.Parse(json);
        }
        catch (JsonReaderException ex)
        {
            this.Context.Logger.LogError("Request body is not valid JSON: {0}", ex.Message);
            return BadRequest("Request body is not valid JSON.");
        }

        if (!TryCoerceMetadataStringsInToken(root, out var coerceError))
        {
            return BadRequest(coerceError);
        }

        var newBody = root.ToString(Newtonsoft.Json.Formatting.None);
        req.Content = new StringContent(newBody, Encoding.UTF8, "application/json");
        req.Content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/json");
        return null;
    }

    private bool TryCoerceMetadataStringsInToken(JToken root, out string errorMessage)
    {
        errorMessage = null;
        if (!(root is JObject jobj))
        {
            return true;
        }

        if (jobj["documents"] is JArray docs)
        {
            foreach (var item in docs)
            {
                if (item is JObject doc && !TryCoerceMetadataProperty(doc, "metadata", out errorMessage))
                {
                    return false;
                }
            }
        }

        return TryCoerceMetadataProperty(jobj, "metadata", out errorMessage);
    }

    private static bool TryCoerceMetadataProperty(JObject obj, string name, out string errorMessage)
    {
        errorMessage = null;
        var tok = obj[name];
        if (tok == null || tok.Type == JTokenType.Null)
        {
            return true;
        }

        if (tok.Type == JTokenType.Object)
        {
            return true;
        }

        if (tok.Type != JTokenType.String)
        {
            errorMessage =
                "Metadata must be a JSON object, or a string containing a JSON object (e.g. {\"key\":\"value\"}).";
            return false;
        }

        var s = tok.Value<string>();
        if (string.IsNullOrWhiteSpace(s))
        {
            obj.Remove(name);
            return true;
        }

        JToken parsed;
        try
        {
            parsed = JToken.Parse(s);
        }
        catch (JsonReaderException)
        {
            errorMessage =
                "Metadata must be valid JSON object syntax, e.g. {\"invoice_id\":\"123\"}. Plain text like foo=bar is not valid.";
            return false;
        }

        if (parsed.Type != JTokenType.Object)
        {
            errorMessage =
                "Metadata must decode to a JSON object with string keys and string values, not an array or primitive.";
            return false;
        }

        obj[name] = parsed;
        return true;
    }

    private static HttpResponseMessage BadRequest(string message)
    {
        var response = new HttpResponseMessage(HttpStatusCode.BadRequest);
        response.Content = CreateJsonContent(new JObject { ["message"] = message }.ToString());
        return response;
    }
}
