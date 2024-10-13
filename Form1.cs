using System;
using System.IO;
using System.Threading.Tasks;
using System.Windows.Forms;
namespace HSAPatcher;
public class MainForm : Form
{
    private TextBox directoryBox = null!;
    private ComboBox cmbChannels = null!;
    private Button btnStart = null!;
    private FlowLayoutPanel mainPanel = null!;
    private OperationPanel operationPanel = null!;

    public MainForm()
    {
        InitializeComponent();
    }

    private void InitializeComponent()
    {
        cmbChannels = new ComboBox();
        btnStart = new Button();
        mainPanel = new FlowLayoutPanel();

        this.Text = "HSAPatcher";
        this.Size = new System.Drawing.Size(600, 400);
        this.StartPosition = FormStartPosition.CenterScreen;

        mainPanel.Dock = DockStyle.Fill;
        mainPanel.FlowDirection = FlowDirection.TopDown;
        mainPanel.Padding = new Padding(10);
        mainPanel.AutoSize = true;
        mainPanel.AutoSizeMode = AutoSizeMode.GrowAndShrink;

        FlowLayoutPanel pickerPanel = new FlowLayoutPanel();
        pickerPanel.AutoSize = true;
        pickerPanel.FlowDirection = FlowDirection.LeftToRight;

        Label lblPath = new Label();
        lblPath.Text = "Select Folder:";
        lblPath.AutoSize = true;

        directoryBox = new TextBox();
        directoryBox.Width = 250;
        directoryBox.ReadOnly = true;

        Button btnBrowse = new Button();
        btnBrowse.Text = "Change:";
        btnBrowse.AutoSize = true;
        btnBrowse.Click += (s, e) =>
        {
            using (FolderBrowserDialog dialog = new FolderBrowserDialog())
            {
                dialog.Description = "Select the folder where Hearthstone is installed:";
                dialog.ShowNewFolderButton = false;
                dialog.OkRequiresInteraction = true;
                dialog.UseDescriptionForTitle = true;
                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    directoryBox.Text = dialog.SelectedPath;
                }
            }
        };

        pickerPanel.Controls.Add(lblPath);
        pickerPanel.Controls.Add(directoryBox);
        pickerPanel.Controls.Add(btnBrowse);

        mainPanel.Controls.Add(pickerPanel);


        FlowLayoutPanel comboPanel = new FlowLayoutPanel();
        comboPanel.FlowDirection = FlowDirection.LeftToRight;
        comboPanel.AutoSize = true;
        comboPanel.AutoSizeMode = AutoSizeMode.GrowAndShrink;

        Label lblSelect = new Label()
        {
            Text = "Select Channel:",
            AutoSize = true,
        };

        cmbChannels.DropDownStyle = ComboBoxStyle.DropDownList;
        cmbChannels.Width = 200;

        foreach (Source source in SourceManager.Sources)
        {
            cmbChannels.Items.Add(source.name);
        }

        comboPanel.Controls.Add(lblSelect);
        comboPanel.Controls.Add(cmbChannels);

        btnStart.Text = "Start";
        btnStart.AutoSize = true;
        btnStart.Margin = new Padding(0, 10, 0, 0); // Add top margin for spacing
        btnStart.Click += BtnStart_Click;

        mainPanel.Controls.Add(comboPanel);
        mainPanel.Controls.Add(btnStart);
        operationPanel = new OperationPanel();

        mainPanel.Controls.Add(operationPanel);
        this.Controls.Add(mainPanel);
        string? path = Patcher.LocateHearthstone();
        if (!string.IsNullOrWhiteSpace(path))
        {
            directoryBox.Text = path;
        }
        else
        {
            MessageBox.Show(this, "Could not automatically locate where Hearthstone is installed to apply the patch. On the next screen, please press on the 'change' button and pick where you've installed Hearthstone by choosing the Hearthstone folder.", "Warning", MessageBoxButtons.OK, MessageBoxIcon.Warning);
        }

        cmbChannels.SelectedIndex = 0;

    }

    private async void BtnStart_Click(object? sender, EventArgs e)
    {
        string directory = directoryBox.Text;
        if (!Patcher.IsHsDirectory(directory))
        {
            MessageBox.Show(this, "The provided path is not a valid directory to a hearthstone installation.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return;
        }

        if (cmbChannels.SelectedIndex < 0)
        {
            MessageBox.Show(this, "No release channel is  selected. Please select a channel.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return;
        }
        Source source = SourceManager.Sources[cmbChannels.SelectedIndex];

        // Disable Start button to prevent multiple clicks
        btnStart.Enabled = false;
        operationPanel.AddHistoryItem($"Selected HearthstoneDirectory: {directory}");
        operationPanel.AddHistoryItem($"Selected channel: {source.name}, at {source.url}");
        operationPanel.LabelText = "Downloading...";
        Downloader downloader = new Downloader(source.url);

        downloader.ProgressChanged += (sender, progress) =>
        {
            operationPanel.UpdateProgress(progress, "Downloading...");
        };
        using Stream stream = await downloader.Download();
        operationPanel.LabelText= "Patching...";
        await Task.Yield();
        Patcher.UnpackAndPatch(stream, directory);

        operationPanel.LabelText = "Done.";
        // Re-enable Start button
        btnStart.Enabled = true;

        MessageBox.Show("Hearthstone patched!", "Done", MessageBoxButtons.OK, MessageBoxIcon.Information);
    }
}
