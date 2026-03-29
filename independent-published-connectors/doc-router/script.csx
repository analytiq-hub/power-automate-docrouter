// Injects the organization ID from the connection into every request path (/v0/orgs/{organization_id}/...).
// Connection parameter docrouter_organization_id is available as a request header (same pattern as
// microsoft/PowerPlatformConnectors certified connectors — e.g. QPP NextGen, Zoho Invoice Basic).
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

    private static HttpResponseMessage BadRequest(string message)
    {
        var response = new HttpResponseMessage(HttpStatusCode.BadRequest);
        response.Content = CreateJsonContent(new JObject { ["message"] = message }.ToString());
        return response;
    }
}
