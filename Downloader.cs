using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using System.Diagnostics;
namespace HSAPatcher;
public class Downloader
{
    private const int bufferSize = 65536;
    public event EventHandler<int>? ProgressChanged;
    public int Progress {get; private set;}
    private int lastPercent;
    private readonly string url;
    private long downloaded;
    private long lastDownloaded;
    private long length;

    public Downloader(string url)
    {
        this.url = url;
    }

    async public Task<MemoryStream> Download()
    {
        using HttpClient client = new HttpClient();
        using HttpResponseMessage response = await client.GetAsync(url, HttpCompletionOption.ResponseHeadersRead);
        response.EnsureSuccessStatusCode();
        length = response.Content.Headers.ContentLength ?? -1L;
        MemoryStream memoryStream = new MemoryStream();
        using var stream = await response.Content.ReadAsStreamAsync();
        byte[] buffer = new byte[bufferSize];
        int read;
        while ((read = await stream.ReadAsync(buffer, 0, buffer.Length)) != 0)
        {
            downloaded += read;
            memoryStream.Write(new ReadOnlySpan<byte>(buffer, 0, read));
            ReportProgress();
        }

        memoryStream.Position = 0;
        return memoryStream;
    }

    private void ReportProgress()
    {
        if (length > 0 && downloaded > 0)
        {
            int percent = (int)((double)downloaded / (double)length * 100);
            if (percent == lastPercent)
            {
                return;
            }
            Progress = percent;
            ProgressChanged?.Invoke(this, Progress);
            // Console.WriteLine($"{percent}%; {GetAppropriateStorageUnit(downloaded)} / {GetAppropriateStorageUnit(length)}");
            lastPercent = percent;
        }
        else
        {
            if (downloaded - lastDownloaded > 65536)
            {
                // Console.WriteLine($"{GetAppropriateStorageUnit(downloaded)}");
                lastDownloaded = downloaded;
            }

        }

    }

    private string GetAppropriateStorageUnit(long bytes)
    {
        if (bytes < 1024)
        {
            return $"{bytes}B";
        }
        else if (bytes < 1048576)
        {
            return $"{Math.Round((double)bytes / 1024, 2)} KB";
        }
        else
        {
            return $"{Math.Round((double)bytes / 1024 / 1024, 2)} MB";
        }
    }



}
