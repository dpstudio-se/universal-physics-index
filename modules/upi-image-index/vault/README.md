# vault/

Store raw image files here for local analysis. **This directory is never committed.**

The `.gitignore` in this directory excludes all image files. Only `README.md` and
`.gitignore` are tracked.

## Usage

```bash
# Copy or download your images here
cp ~/Downloads/my_image.png vault/

# Index the image (writes a JSON node to data/images/)
upi-img index vault/my_image.png \
  --address "UPI<IMAGE,1,MY_TORUS,MY_NODE>" \
  --title "My image" \
  --status SYM \
  --tokens "TF,DNA,TORUS,8 HZ"

# Run shadow analysis
upi-img shadow vault/my_image.png
```

## Security

- Never commit image files that contain private or sensitive content
- The extractor reports only derived statistics, hashes, and text tokens
- Raw pixel values are never written to index JSON files
