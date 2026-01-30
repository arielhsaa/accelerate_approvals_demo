# How to Use the Presentation

## 📊 PRESENTATION.md - Slide Deck for Payment Authorization Demo

This presentation is in **Marp format** - a markdown-based presentation tool that creates beautiful slides.

---

## 🎯 Quick Start

### Option 1: Use Marp CLI (Recommended)

```bash
# Install Marp CLI
npm install -g @marp-team/marp-cli

# Generate HTML slides
marp PRESENTATION.md -o presentation.html

# Generate PDF
marp PRESENTATION.md -o presentation.pdf

# Live preview with auto-reload
marp -w PRESENTATION.md
```

### Option 2: Use Marp for VS Code/Cursor

1. Install the **Marp for VS Code** extension
2. Open `PRESENTATION.md`
3. Click the preview button or press `Ctrl+Shift+V`
4. Export as HTML or PDF from the preview

### Option 3: Use Online Viewers

Upload to:
- [Marp Web](https://web.marp.app/) - Online editor & preview
- [HackMD](https://hackmd.io/) - Collaborative markdown with Marp support

---

## 📖 Presentation Structure (30 slides)

### Introduction (Slides 1-3)
- Title slide with branding
- The business challenge ($118B problem)
- Solution overview (3 core capabilities)

### Smart Checkout (Slides 4-6)
- How it works (50+ combinations)
- Real example with transaction flow
- Business impact

### Reason Code Analytics (Slides 7-9)
- Real-time insights
- Example actionable insight
- Decline analysis dashboard

### Smart Retry (Slides 10-12)
- ML-powered optimization
- Example retry scenario
- Success metrics

### Architecture (Slide 13)
- Bronze/Silver/Gold pipeline
- Technology stack

### Business Impact (Slides 14-15)
- ROI metrics
- Financial impact
- Risk management

### Command Center (Slides 16-17)
- Live monitoring dashboard
- Interactive features
- Screenshot/mockup

### Use Case (Slide 18)
- Enterprise example (PayFlow)
- Before/after comparison

### What's Included (Slide 19)
- Notebooks, configs, docs

### Getting Started (Slide 20)
- 30-minute quickstart

### Demo Scenarios (Slide 21)
- For executives, technical teams, PMs

### Future Enhancements (Slide 22)
- Phase 2, 3, 4 roadmap

### Technical Details (Slide 23)
- Performance, reliability, cost

### Success Metrics (Slide 24)
- Operational, financial, technical KPIs

### Why Databricks (Slide 25)
- Unified Lakehouse benefits

### Who Benefits (Slide 26)
- Target audiences

### Next Steps (Slide 27)
- Call to action

### Q&A (Slide 28)
- Questions slide

---

## 🎨 Customization

### Change Theme

Edit the front matter (top of file):

```yaml
---
theme: default  # Options: default, gaia, uncover
---
```

### Change Colors

Modify the `style` section:

```yaml
style: |
  h1 {
    color: #FF3621;  # Your brand color
  }
```

### Add Your Logo

```yaml
backgroundImage: url('https://your-logo-url.com/logo.png')
```

---

## 📊 Presentation Tips

### For 15-Minute Executive Demo
Use slides: 1-3, 4, 7, 10, 14-15, 18, 27-28

### For 30-Minute Product Demo
Use slides: 1-6, 7-9, 10-12, 14-18, 20, 27-28

### For 45-Minute Technical Deep-Dive
Use all slides: 1-28

### For 60-Minute Workshop
Use all slides + live demo in Databricks

---

## 🖼️ Export Formats

### HTML (Interactive)
```bash
marp PRESENTATION.md -o presentation.html
# Open in browser for presenting
```

### PDF (Print/Share)
```bash
marp PRESENTATION.md -o presentation.pdf
# Share via email or print
```

### PowerPoint (Editable)
```bash
marp PRESENTATION.md -o presentation.pptx --allow-local-files
# Edit in PowerPoint/Keynote
```

---

## 📱 Presenting

### Keyboard Shortcuts
- **Arrow keys** or **Space**: Next/previous slide
- **F**: Fullscreen
- **S**: Speaker notes (if added)
- **Esc**: Exit fullscreen

### Tips
- Practice the flow beforehand
- Use examples from DEMO_SCRIPT.md
- Have Databricks App open in another tab for live demo
- Prepare for Q&A with FAQ from README.md

---

## 🔧 Troubleshooting

### "marp: command not found"
Install Marp CLI: `npm install -g @marp-team/marp-cli`

### Styling not working
Make sure the YAML front matter is at the very top of the file

### Images not showing
Use absolute URLs or enable `--allow-local-files` flag

---

## 📚 Resources

- **Marp Official Site**: https://marp.app/
- **Marp CLI Docs**: https://github.com/marp-team/marp-cli
- **VS Code Extension**: Search "Marp for VS Code" in extensions
- **Examples**: https://github.com/marp-team/marp/tree/main/examples

---

## 🎯 Next Steps

1. **Preview the presentation**: Open in Marp or export to HTML
2. **Customize branding**: Update colors, logo, company name
3. **Practice delivery**: Use with DEMO_SCRIPT.md
4. **Prepare demos**: Have Databricks App and notebooks ready
5. **Create handouts**: Export to PDF for audience

**Good luck with your presentation! 🚀**
