from image_analysis import perform_ela


image_path = "data/sample_documents/sample_passport.png"

ela_image = perform_ela(image_path)

output_path = "data/sample_documents/ela_result.jpg"

ela_image.save(output_path)

print("ELA analysis completed.")
print(f"Result saved to: {output_path}")